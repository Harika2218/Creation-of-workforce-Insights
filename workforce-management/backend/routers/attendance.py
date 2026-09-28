"""
Attendance Router
-----------------
Handles check-in, check-out, geofencing, anomaly tracking, history, and summaries.
"""

from datetime import datetime, date, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.schemas.common import PaginatedResponse, MessageResponse
from backend.schemas.attendance import (
    CheckInRequest, CheckOutRequest, AttendanceResponse, AttendanceSummaryResponse
)
from backend.auth.dependencies import get_current_user, require_role
from backend.utils.geofence import is_within_geofence, validate_multi_campus_geofence, detect_impossible_movement
from backend.events.events import HREventType
from backend.events.dispatcher import dispatch_event

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/check-in", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED, summary="Record employee clock-in")
async def clock_in(payload: CheckInRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    # RBAC: Employees can only check in for themselves unless HR/Admin
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != payload.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only clock in for yourself."
        )

    emp = db.employees.find_one({"employee_id": payload.employee_id})
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{payload.employee_id}' not found."
        )

    today_str = date.today().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    # Duplicate check-in prevention
    existing = db.attendance.find_one({
        "employee_id": payload.employee_id,
        "date": today_str
    })
    if existing and existing.get("check_in"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee '{payload.employee_id}' has already clocked in today at {existing['check_in']}."
        )

    # Advanced GPS Geofence validation (Multi-campus & Impossible movement)
    anomaly_flag = 0
    anomaly_reason = None
    if payload.attendance_method == "GPS" and payload.location:
        assigned_loc = db.locations.find_one({"location_id": emp["location_id"]})
        all_locs = list(db.locations.find({}, {"_id": 0}))
        if assigned_loc:
            geo_res = validate_multi_campus_geofence(
                payload.location.latitude, payload.location.longitude,
                assigned_loc, all_locs
            )
            if not geo_res["valid"]:
                anomaly_flag = 1
                anomaly_reason = f"GPS Geofence Violation: Clock-in {geo_res['distance_meters']}m from office hub (Allowed: {geo_res['allowed_radius']}m)."

        # Check for impossible physical movement from recent punch
        prev_att = db.attendance.find_one(
            {"employee_id": payload.employee_id, "check_in_location": {"$exists": True}},
            sort=[("date", -1)]
        )
        if prev_att and prev_att.get("check_in_location"):
            p_lat = prev_att["check_in_location"].get("latitude")
            p_lon = prev_att["check_in_location"].get("longitude")
            p_time = prev_att.get("created_at") or f"{prev_att['date']}T09:00:00Z"
            now_iso = datetime.now(timezone.utc).isoformat()
            if p_lat is not None and p_lon is not None:
                is_impossible, speed_kmh, dist_km = detect_impossible_movement(
                    p_lat, p_lon, p_time,
                    payload.location.latitude, payload.location.longitude, now_iso
                )
                if is_impossible:
                    anomaly_flag = 1
                    anomaly_reason = f"Suspicious Teleportation: Traveled {dist_km}km at {speed_kmh}km/h between consecutive punches."

    # Determine shift and late arrival
    shift_id = payload.shift_id or "SH01"
    shift = db.shifts.find_one({"shift_id": shift_id})
    late_minutes = 0
    att_status = "Present"
    if shift:
        s_start_h, s_start_m = map(int, shift["start_time"].split(":"))
        now_h, now_m, _ = map(int, now_time.split(":"))
        in_mins = now_h * 60 + now_m
        shift_mins = s_start_h * 60 + s_start_m + shift.get("grace_period_mins", 15)
        if in_mins > shift_mins:
            late_minutes = in_mins - (s_start_h * 60 + s_start_m)
            att_status = "Late"

    attendance_id = f"ATT_{payload.employee_id}_{today_str.replace('-', '')}"
    att_doc = {
        "attendance_id": attendance_id,
        "employee_id": payload.employee_id,
        "date": today_str,
        "check_in": now_time,
        "check_out": None,
        "attendance_status": att_status,
        "attendance_method": payload.attendance_method,
        "location_id": emp["location_id"],
        "late_minutes": late_minutes,
        "overtime_hours": 0.0,
        "shift_id": shift_id,
        "anomaly_flag": anomaly_flag,
        "anomaly_reason": anomaly_reason
    }

    if existing:
        db.attendance.update_one({"attendance_id": existing["attendance_id"]}, {"$set": att_doc})
    else:
        db.attendance.insert_one(att_doc)

    # Also log to attendance_anomalies if flagged
    if anomaly_flag == 1:
        db.attendance_anomalies.replace_one(
            {"attendance_id": attendance_id},
            {
                "anomaly_id": f"ANO_{attendance_id}",
                "attendance_id": attendance_id,
                "employee_id": payload.employee_id,
                "date": today_str,
                "anomaly_type": "GEOFENCE",
                "reason": anomaly_reason,
                "severity": "HIGH",
                "status": "Investigating"
            },
            upsert=True
        )

    # Phase 7: Dispatch Attendance Events
    emp_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip()
    if att_status == "Late":
        dispatch_event(
            event_type=HREventType.LATE_ARRIVAL,
            entity_type="attendance",
            entity_id=attendance_id,
            target_employee_id=payload.employee_id,
            payload={
                "employee_id": payload.employee_id,
                "employee_name": emp_name,
                "late_minutes": late_minutes,
                "shift_name": shift.get("shift_name", "General Shift") if shift else "Scheduled Shift",
                "time": now_time
            },
            dedup_key=f"LATE_{payload.employee_id}_{today_str}"
        )
    if anomaly_flag == 1:
        dispatch_event(
            event_type=HREventType.ATTENDANCE_ANOMALY,
            entity_type="attendance",
            entity_id=attendance_id,
            target_employee_id=payload.employee_id,
            payload={
                "employee_id": payload.employee_id,
                "employee_name": emp_name,
                "reason": anomaly_reason,
                "time": now_time
            },
            dedup_key=f"ATT_ANO_{payload.employee_id}_{today_str}"
        )

    att_doc.pop("_id", None)
    return att_doc

@router.post("/check-out", response_model=AttendanceResponse, summary="Record employee clock-out")
async def clock_out(payload: CheckOutRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != payload.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only clock out for yourself."
        )

    today_str = date.today().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    existing = db.attendance.find_one({
        "employee_id": payload.employee_id,
        "date": today_str
    })
    if not existing or not existing.get("check_in"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot clock out: No clock-in record found today for '{payload.employee_id}'."
        )

    # Calculate hours worked and overtime
    in_h, in_m, in_s = map(int, existing["check_in"].split(":"))
    out_h, out_m, out_s = map(int, now_time.split(":"))

    in_total_sec = in_h * 3600 + in_m * 60 + in_s
    out_total_sec = out_h * 3600 + out_m * 60 + out_s

    if out_total_sec <= in_total_sec:
        # Wrap past midnight allowance or reject
        out_total_sec += 24 * 3600

    hours_worked = round((out_total_sec - in_total_sec) / 3600.0, 2)
    overtime_hours = round(max(0.0, hours_worked - 8.0), 2)

    db.attendance.update_one(
        {"attendance_id": existing["attendance_id"]},
        {"$set": {
            "check_out": now_time,
            "overtime_hours": overtime_hours
        }}
    )

    updated = db.attendance.find_one({"attendance_id": existing["attendance_id"]}, {"_id": 0})

    # Phase 7: Dispatch Overtime / Checkout Events
    emp = db.employees.find_one({"employee_id": payload.employee_id})
    emp_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip() if emp else payload.employee_id
    if overtime_hours >= 2.0:
        dispatch_event(
            event_type=HREventType.OVERTIME_DETECTED,
            entity_type="attendance",
            entity_id=existing["attendance_id"],
            target_employee_id=payload.employee_id,
            payload={
                "employee_id": payload.employee_id,
                "employee_name": emp_name,
                "overtime_hours": overtime_hours,
                "hours_worked": hours_worked
            },
            dedup_key=f"OVERTIME_{payload.employee_id}_{today_str}"
        )

    return updated

@router.get("", response_model=PaginatedResponse[AttendanceResponse], summary="List attendance logs with filtering & pagination")
async def list_attendance(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    employee_id: Optional[str] = Query(None),
    date_val: Optional[str] = Query(None, alias="date"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status_val: Optional[str] = Query(None, alias="status"),
    attendance_method: Optional[str] = Query(None),
    anomaly_only: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    query = {}

    # Scoping for EMPLOYEE role: can only view own attendance
    if current_user.get("role") == "EMPLOYEE":
        query["employee_id"] = current_user.get("employee_id")
    elif employee_id:
        query["employee_id"] = employee_id

    if date_val:
        query["date"] = date_val
    elif start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        query["date"] = {"$gte": start_date}

    if status_val:
        query["attendance_status"] = status_val
    if attendance_method:
        query["attendance_method"] = attendance_method
    if anomaly_only:
        query["anomaly_flag"] = 1

    total = db.attendance.count_documents(query)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    skip = (page - 1) * page_size

    logs = list(db.attendance.find(query, {"_id": 0}).sort("date", -1).skip(skip).limit(page_size))

    return {
        "data": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/summary", response_model=AttendanceSummaryResponse, summary="Get aggregated attendance metrics")
async def attendance_summary(
    employee_id: Optional[str] = Query(None),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    match_stage = {}
    if current_user.get("role") == "EMPLOYEE":
        match_stage["employee_id"] = current_user.get("employee_id")
    elif employee_id:
        match_stage["employee_id"] = employee_id

    if month:
        match_stage["date"] = {"$regex": f"^{month}"}

    total_days = db.attendance.count_documents(match_stage)
    present_days = db.attendance.count_documents({**match_stage, "attendance_status": "Present"})
    absent_days = db.attendance.count_documents({**match_stage, "attendance_status": "Absent"})
    late_days = db.attendance.count_documents({**match_stage, "attendance_status": "Late"})
    half_days = db.attendance.count_documents({**match_stage, "attendance_status": "Half Day"})
    wfh_days = db.attendance.count_documents({**match_stage, "attendance_status": "Work From Home"})
    leave_days = db.attendance.count_documents({**match_stage, "attendance_status": "Leave"})

    pipeline = [
        {"$match": match_stage},
        {"$group": {"_id": None, "total_ot": {"$sum": "$overtime_hours"}}}
    ]
    ot_res = list(db.attendance.aggregate(pipeline))
    total_ot = ot_res[0]["total_ot"] if ot_res else 0.0

    working_attendance = present_days + late_days + half_days + wfh_days
    pct = round((working_attendance / max(1, total_days)) * 100, 1)

    return {
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "late_days": late_days,
        "half_days": half_days,
        "wfh_days": wfh_days,
        "leave_days": leave_days,
        "total_overtime_hours": round(total_ot, 1),
        "attendance_percentage": pct
    }

@router.get("/{employee_id}", response_model=PaginatedResponse[AttendanceResponse], summary="Get attendance history for an employee")
async def get_employee_attendance(
    employee_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    # RBAC: Employee can only access their own attendance
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to view another employee's attendance."
        )

    db = get_db()
    query = {"employee_id": employee_id}
    total = db.attendance.count_documents(query)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    skip = (page - 1) * page_size

    logs = list(db.attendance.find(query, {"_id": 0}).sort("date", -1).skip(skip).limit(page_size))

    return {
        "data": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }
