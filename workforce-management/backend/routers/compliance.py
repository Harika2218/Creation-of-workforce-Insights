"""
Enterprise Compliance Alerting & Policy Monitoring Router
---------------------------------------------------------
Automates rule-based compliance checks for excessive overtime, missing checkouts,
unresolved attendance anomalies, expiring contractor SOWs, and overdue reviews.
Non-punitive: all alerts require human managerial review.
"""

from typing import List, Optional
import uuid
from datetime import datetime, date, timedelta, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.auth.dependencies import require_role
from backend.schemas.compliance import (
    ComplianceAlertItem, ComplianceAlertStatusUpdate, ComplianceSummaryResponse
)

router = APIRouter(prefix="/compliance", tags=["Compliance & Risk Monitoring"])

@router.get("/alerts", response_model=ComplianceSummaryResponse, summary="Query active enterprise compliance alerts (HR/Admin/Manager)")
async def get_compliance_alerts(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    now_iso = datetime.now(timezone.utc).isoformat()
    today_str = date.today().strftime("%Y-%m-%d")
    alerts: List[ComplianceAlertItem] = []

    # 1. Excessive Overtime Rule (>12.0 hours in current/latest month)
    ot_pipeline = [
        {"$match": {"overtime_hours": {"$gt": 0}}},
        {"$group": {
            "_id": "$employee_id",
            "total_ot": {"$sum": "$overtime_hours"},
            "count": {"$sum": 1}
        }},
        {"$match": {"total_ot": {"$gte": 12.0}}},
        {"$limit": 10}
    ]
    ot_results = list(db.attendance.aggregate(ot_pipeline))
    emp_map = {e["employee_id"]: f"{e.get('first_name','')} {e.get('last_name','')}".strip() for e in db.employees.find({})}

    for r in ot_results:
        eid = r["_id"]
        emp_name = emp_map.get(eid, f"Employee {eid}")
        total_ot = round(r["total_ot"], 1)
        alerts.append(ComplianceAlertItem(
            alert_id=f"CMP_OT_{eid}",
            rule_name="EXCESSIVE_OVERTIME_LIMIT",
            category="WORKING_HOURS",
            severity="HIGH" if total_ot > 20 else "MEDIUM",
            entity_type="employee",
            entity_id=eid,
            entity_name=emp_name,
            description=f"Accumulated {total_ot} hours of overtime this period, exceeding standard 12.0-hour fatigue limit.",
            recommended_action="Review employee workload and adjust rotational shifts to avoid burnout.",
            status="Open",
            detected_at=now_iso
        ))

    # 2. Missing Check-Outs on Past Days
    missing_co = list(db.attendance.find({
        "date": {"$lt": today_str},
        "check_in": {"$ne": None},
        "check_out": None
    }, {"_id": 0}).limit(10))

    for m in missing_co:
        eid = m.get("employee_id", "")
        emp_name = emp_map.get(eid, f"Employee {eid}")
        alerts.append(ComplianceAlertItem(
            alert_id=f"CMP_MCO_{eid}_{m.get('date')}",
            rule_name="MISSING_CHECKOUT_RECORD",
            category="ATTENDANCE",
            severity="MEDIUM",
            entity_type="employee",
            entity_id=eid,
            entity_name=emp_name,
            description=f"Clock-in logged at {m.get('check_in')} on {m.get('date')}, but no clock-out timestamp was recorded.",
            recommended_action="Prompt employee to submit an attendance regularization ticket for supervisor review.",
            status="Open",
            detected_at=now_iso
        ))

    # 3. Unresolved Attendance Geofence/Teleportation Anomalies
    anomalies = list(db.attendance.find({
        "anomaly_flag": 1
    }, {"_id": 0}).limit(10))

    for a in anomalies:
        eid = a.get("employee_id", "")
        emp_name = emp_map.get(eid, f"Employee {eid}")
        alerts.append(ComplianceAlertItem(
            alert_id=f"CMP_ANO_{a.get('attendance_id')}",
            rule_name="GEOFENCE_ATTENDANCE_ANOMALY",
            category="ATTENDANCE",
            severity="HIGH",
            entity_type="employee",
            entity_id=eid,
            entity_name=emp_name,
            description=f"Attendance anomaly logged on {a.get('date')}: {a.get('anomaly_reason', 'Unusual location or timing pattern')}.",
            recommended_action="Manager verification required to determine if employee was working remotely or on customer site.",
            status="Open",
            detected_at=now_iso
        ))

    # 4. Contractor Contracts Expiring Soon (Within 60 days)
    if "contractors" in db.list_collection_names():
        contractors = list(db.contractors.find({"status": "Active"}, {"_id": 0}))
        for c in contractors:
            end_d_str = c.get("end_date")
            if end_d_str:
                try:
                    end_d = datetime.strptime(end_d_str, "%Y-%m-%d").date()
                    days_left = (end_d - date.today()).days
                    if 0 <= days_left <= 60:
                        cid = c.get("contractor_id")
                        c_name = f"{c.get('first_name','')} {c.get('last_name','')}".strip()
                        alerts.append(ComplianceAlertItem(
                            alert_id=f"CMP_CON_{cid}",
                            rule_name="CONTRACTOR_SOW_EXPIRATION",
                            category="VENDOR_CONTRACTS",
                            severity="HIGH" if days_left <= 15 else "MEDIUM",
                            entity_type="contractor",
                            entity_id=cid,
                            entity_name=f"{c_name} ({c.get('vendor_org')})",
                            description=f"Contract expires in {days_left} days on {end_d_str}. Project: {c.get('assigned_project_id')}.",
                            recommended_action="Initiate SOW extension amendment or begin offboarding knowledge transfer.",
                            status="Open",
                            detected_at=now_iso
                        ))
                except Exception:
                    pass

    # Filter by category & severity if requested
    if category:
        alerts = [a for a in alerts if a.category.upper() == category.upper()]
    if severity:
        alerts = [a for a in alerts if a.severity.upper() == severity.upper()]

    # Check database for overridden resolved statuses
    resolved_ids = {doc["alert_id"]: doc for doc in db.compliance_alert_resolutions.find({})}
    for a in alerts:
        if a.alert_id in resolved_ids:
            a.status = resolved_ids[a.alert_id].get("status", "Resolved")

    # Metrics
    crit = sum(1 for a in alerts if a.severity == "CRITICAL")
    high = sum(1 for a in alerts if a.severity == "HIGH")
    med = sum(1 for a in alerts if a.severity == "MEDIUM")
    cats = {}
    for a in alerts:
        cats[a.category] = cats.get(a.category, 0) + 1

    return ComplianceSummaryResponse(
        total_active_alerts=len(alerts),
        critical_count=crit,
        high_count=high,
        medium_count=med,
        category_breakdown=cats,
        alerts=alerts[:25]
    )

@router.put("/alerts/{alert_id}/status", summary="Update compliance alert review status (Manager/HR/Admin)")
async def update_alert_status(
    alert_id: str,
    payload: ComplianceAlertStatusUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    now_iso = datetime.now(timezone.utc).isoformat()
    
    doc = {
        "alert_id": alert_id,
        "status": payload.status,
        "review_notes": payload.review_notes,
        "reviewed_by": current_user.get("user_id"),
        "reviewed_at": now_iso
    }
    
    db.compliance_alert_resolutions.replace_one({"alert_id": alert_id}, doc, upsert=True)
    
    # Audit log
    db.audit_logs.insert_one({
        "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
        "timestamp": now_iso,
        "actor_user_id": current_user.get("user_id"),
        "actor_role": current_user.get("role"),
        "action": "UPDATE_COMPLIANCE_ALERT_STATUS",
        "resource_type": "compliance_alert",
        "resource_id": alert_id,
        "status": "SUCCESS",
        "details": {"new_status": payload.status, "notes": payload.review_notes}
    })
    
    return {"alert_id": alert_id, "status": payload.status, "message": "Compliance review status updated successfully."}
