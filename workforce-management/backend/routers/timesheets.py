"""
Timesheets Router
-----------------
Daily project work log submissions and manager approval workflows.
"""

from typing import Optional
import uuid
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.schemas.timesheets import (
    TimesheetCreate, TimesheetUpdate, TimesheetResponse, TimesheetApprovalAction
)
from backend.schemas.common import PaginatedResponse, MessageResponse
from backend.auth.dependencies import get_current_user, require_role
from backend.events.events import HREventType
from backend.events.dispatcher import dispatch_event

router = APIRouter(prefix="/timesheets", tags=["Timesheets"])

@router.get("", response_model=PaginatedResponse[TimesheetResponse], summary="List timesheets with filtering & pagination")
async def list_timesheets(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    employee_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    date_val: Optional[str] = Query(None, alias="date"),
    status_val: Optional[str] = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    query = {}

    user_role = current_user.get("role", "EMPLOYEE")
    if user_role == "EMPLOYEE":
        query["employee_id"] = current_user.get("employee_id")
    elif user_role == "MANAGER":
        team_ids = db.employees.distinct("employee_id", {"manager_id": current_user.get("employee_id")})
        team_ids.append(current_user.get("employee_id"))
        query["employee_id"] = {"$in": team_ids}
    elif employee_id:
        query["employee_id"] = employee_id

    if project_id:
        query["project_id"] = project_id
    if date_val:
        query["date"] = date_val
    if status_val:
        query["status"] = status_val

    total = db.timesheets.count_documents(query)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    skip = (page - 1) * page_size

    entries = list(db.timesheets.find(query, {"_id": 0}).sort("date", -1).skip(skip).limit(page_size))

    return {
        "data": entries,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.post("", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED, summary="Log project timesheet entry")
async def create_timesheet(payload: TimesheetCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != payload.employee_id:
        raise HTTPException(status_code=403, detail="You can only submit timesheets for yourself.")

    if not db.employees.find_one({"employee_id": payload.employee_id}):
        raise HTTPException(status_code=404, detail=f"Employee '{payload.employee_id}' not found.")

    if not db.projects.find_one({"project_id": payload.project_id}):
        raise HTTPException(status_code=404, detail=f"Project '{payload.project_id}' not found.")

    # Validation: billable + non_billable == hours_worked
    if abs((payload.billable_hours + payload.non_billable_hours) - payload.hours_worked) > 0.05:
        raise HTTPException(
            status_code=400,
            detail=f"Discrepancy: Billable ({payload.billable_hours}h) + Non-Billable ({payload.non_billable_hours}h) must equal Total Hours Worked ({payload.hours_worked}h)."
        )

    ts_id = f"TS_{uuid.uuid4().hex[:6].upper()}"
    ts_doc = payload.model_dump()
    ts_doc.update({
        "timesheet_id": ts_id,
        "status": "Submitted"
    })

    db.timesheets.insert_one(ts_doc)
    ts_doc.pop("_id", None)

    # Phase 7: Dispatch Timesheet Submitted Event
    emp = db.employees.find_one({"employee_id": payload.employee_id})
    emp_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip() if emp else payload.employee_id
    dispatch_event(
        event_type=HREventType.TIMESHEET_SUBMITTED,
        entity_type="timesheet",
        entity_id=ts_id,
        target_employee_id=payload.employee_id,
        payload={
            "employee_id": payload.employee_id,
            "employee_name": emp_name,
            "project_id": payload.project_id,
            "total_hours": payload.hours_worked,
            "date": payload.date
        },
        dedup_key=f"TS_SUBMIT_{ts_id}"
    )

    return ts_doc

@router.get("/{timesheet_id}", response_model=TimesheetResponse, summary="Get single timesheet entry")
async def get_timesheet(timesheet_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    ts = db.timesheets.find_one({"timesheet_id": timesheet_id}, {"_id": 0})
    if not ts:
        raise HTTPException(status_code=404, detail=f"Timesheet '{timesheet_id}' not found.")
    return ts

@router.post("/{timesheet_id}/approve", response_model=TimesheetResponse, summary="Approve timesheet entry (Manager/HR/Admin only)")
async def approve_timesheet(timesheet_id: str, current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    ts = db.timesheets.find_one({"timesheet_id": timesheet_id})
    if not ts:
        raise HTTPException(status_code=404, detail=f"Timesheet '{timesheet_id}' not found.")

    db.timesheets.update_one({"timesheet_id": timesheet_id}, {"$set": {"status": "Approved"}})

    # Record in timesheet_approvals
    approver = current_user.get("employee_id") or "ADMIN"
    db.timesheet_approvals.replace_one(
        {"timesheet_id": timesheet_id},
        {
            "approval_id": f"TSA_{timesheet_id}",
            "timesheet_id": timesheet_id,
            "approver_id": approver,
            "status": "Approved",
            "comments": "Approved by reporting manager."
        },
        upsert=True
    )

    dispatch_event(
        event_type=HREventType.TIMESHEET_APPROVED,
        entity_type="timesheet",
        entity_id=timesheet_id,
        target_employee_id=ts["employee_id"],
        payload={"date": ts.get("date", "recent"), "project_id": ts.get("project_id")},
        dedup_key=f"TS_APP_{timesheet_id}"
    )

    return db.timesheets.find_one({"timesheet_id": timesheet_id}, {"_id": 0})

@router.post("/{timesheet_id}/reject", response_model=TimesheetResponse, summary="Reject timesheet entry (Manager/HR/Admin only)")
async def reject_timesheet(
    timesheet_id: str,
    action: TimesheetApprovalAction,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    ts = db.timesheets.find_one({"timesheet_id": timesheet_id})
    if not ts:
        raise HTTPException(status_code=404, detail=f"Timesheet '{timesheet_id}' not found.")

    db.timesheets.update_one(
        {"timesheet_id": timesheet_id},
        {"$set": {"status": "Rejected", "rejection_reason": action.rejection_reason}}
    )

    approver = current_user.get("employee_id") or "ADMIN"
    db.timesheet_approvals.replace_one(
        {"timesheet_id": timesheet_id},
        {
            "approval_id": f"TSA_{timesheet_id}",
            "timesheet_id": timesheet_id,
            "approver_id": approver,
            "status": "Rejected",
            "comments": action.rejection_reason or "Hours require revision"
        },
        upsert=True
    )

    dispatch_event(
        event_type=HREventType.TIMESHEET_REJECTED,
        entity_type="timesheet",
        entity_id=timesheet_id,
        target_employee_id=ts["employee_id"],
        payload={"reason": action.rejection_reason, "project_id": ts.get("project_id")},
        dedup_key=f"TS_REJ_{timesheet_id}"
    )

    return db.timesheets.find_one({"timesheet_id": timesheet_id}, {"_id": 0})
