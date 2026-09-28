"""
Leave Management Router
-----------------------
Handles leave balances, leave applications, manager approval/rejection workflows.
"""

from typing import List, Optional
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.schemas.leave import (
    LeaveRequestCreate, LeaveApprovalAction, LeaveResponse, LeaveBalanceResponse
)
from backend.schemas.common import PaginatedResponse, MessageResponse
from backend.auth.dependencies import get_current_user, require_role
from backend.events.events import HREventType
from backend.events.dispatcher import dispatch_event

router = APIRouter(prefix="/leave", tags=["Leave"])

@router.get("/types", summary="List available leave categories")
async def list_leave_types(current_user: dict = Depends(get_current_user)):
    db = get_db()
    return list(db.leave_types.find({}, {"_id": 0}))

@router.get("/balance/{employee_id}", response_model=List[LeaveBalanceResponse], summary="Get employee leave balances")
async def get_leave_balance(employee_id: str, current_user: dict = Depends(get_current_user)):
    # RBAC: Employee can only see their own balance unless Manager/HR/Admin
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != employee_id:
        raise HTTPException(status_code=403, detail="Cannot view another employee's leave balance.")

    db = get_db()
    balances = list(db.leave_balances.find({"employee_id": employee_id}, {"_id": 0}))
    return balances

@router.get("/requests", response_model=PaginatedResponse[LeaveResponse], summary="List leave requests with status filter & pagination")
async def list_leave_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[str] = Query(None),
    status_val: Optional[str] = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    query = {}

    # Scoping
    user_role = current_user.get("role", "EMPLOYEE")
    if user_role == "EMPLOYEE":
        query["employee_id"] = current_user.get("employee_id")
    elif user_role == "MANAGER":
        # Can see team's leave requests
        team_ids = db.employees.distinct("employee_id", {"manager_id": current_user.get("employee_id")})
        team_ids.append(current_user.get("employee_id"))
        query["employee_id"] = {"$in": team_ids}
    elif employee_id:
        query["employee_id"] = employee_id

    if status_val:
        query["status"] = status_val

    total = db.leave_requests.count_documents(query)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    skip = (page - 1) * page_size

    requests = list(db.leave_requests.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(page_size))

    return {
        "data": requests,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.post("/requests", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED, summary="Submit a leave application")
async def apply_leave(payload: LeaveRequestCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != payload.employee_id:
        raise HTTPException(status_code=403, detail="You can only apply for leave for yourself.")

    emp = db.employees.find_one({"employee_id": payload.employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{payload.employee_id}' not found.")

    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before or equal to end date.")

    # Check leave balance
    balance = db.leave_balances.find_one({
        "employee_id": payload.employee_id,
        "leave_type": payload.leave_type
    })
    if balance and balance.get("remaining_days", 0) < payload.days_count:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient {payload.leave_type} balance. Requested: {payload.days_count} days, Available: {balance.get('remaining_days')} days."
        )

    leave_id = f"LV_{uuid.uuid4().hex[:6].upper()}"
    leave_doc = payload.model_dump()
    leave_doc.update({
        "leave_id": leave_id,
        "status": "Pending",
        "approved_by": emp.get("manager_id"),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    })

    db.leave_requests.insert_one(leave_doc)
    leave_doc.pop("_id", None)

    # Phase 7: Dispatch Leave Request Event
    emp_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip()
    dispatch_event(
        event_type=HREventType.LEAVE_REQUEST_CREATED,
        entity_type="leave_request",
        entity_id=leave_id,
        target_employee_id=payload.employee_id,
        payload={
            "employee_id": payload.employee_id,
            "employee_name": emp_name,
            "leave_type": payload.leave_type,
            "days_count": payload.days_count,
            "start_date": payload.start_date,
            "end_date": payload.end_date,
            "reason": payload.reason
        },
        dedup_key=f"LEAVE_REQ_{leave_id}"
    )

    return leave_doc

@router.get("/requests/{leave_id}", response_model=LeaveResponse, summary="Get single leave request details")
async def get_leave_request(leave_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    req = db.leave_requests.find_one({"leave_id": leave_id}, {"_id": 0})
    if not req:
        raise HTTPException(status_code=404, detail=f"Leave request '{leave_id}' not found.")
    return req

@router.post("/requests/{leave_id}/approve", response_model=LeaveResponse, summary="Approve leave request (Manager/HR/Admin only)")
async def approve_leave(leave_id: str, current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    req = db.leave_requests.find_one({"leave_id": leave_id})
    if not req:
        raise HTTPException(status_code=404, detail=f"Leave request '{leave_id}' not found.")

    if req.get("status") == "Approved":
        raise HTTPException(status_code=400, detail="Leave request has already been approved.")

    # Update request
    approver_id = current_user.get("employee_id") or "ADMIN"
    db.leave_requests.update_one(
        {"leave_id": leave_id},
        {"$set": {"status": "Approved", "approved_by": approver_id}}
    )

    # Deduct from leave balance
    db.leave_balances.update_one(
        {"employee_id": req["employee_id"], "leave_type": req["leave_type"]},
        {
            "$inc": {"used_days": req["days_count"], "remaining_days": -req["days_count"]}
        }
    )

    # Generate notification for employee via Event Bus
    emp = db.employees.find_one({"employee_id": req["employee_id"]})
    emp_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip() if emp else req["employee_id"]
    dispatch_event(
        event_type=HREventType.LEAVE_APPROVED,
        entity_type="leave_request",
        entity_id=leave_id,
        target_employee_id=req["employee_id"],
        payload={
            "employee_id": req["employee_id"],
            "employee_name": emp_name,
            "leave_type": req["leave_type"],
            "days_count": req["days_count"],
            "start_date": req["start_date"],
            "approver_id": approver_id
        },
        dedup_key=f"LEAVE_APP_{leave_id}"
    )

    return db.leave_requests.find_one({"leave_id": leave_id}, {"_id": 0})

@router.post("/requests/{leave_id}/reject", response_model=LeaveResponse, summary="Reject leave request with reason (Manager/HR/Admin only)")
async def reject_leave(
    leave_id: str,
    action: LeaveApprovalAction,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    req = db.leave_requests.find_one({"leave_id": leave_id})
    if not req:
        raise HTTPException(status_code=404, detail=f"Leave request '{leave_id}' not found.")

    approver_id = current_user.get("employee_id") or "ADMIN"
    reason = action.rejection_reason or "Operational exigencies require workforce presence."

    db.leave_requests.update_one(
        {"leave_id": leave_id},
        {"$set": {
            "status": "Rejected",
            "approved_by": approver_id,
            "rejection_reason": reason
        }}
    )

    emp = db.employees.find_one({"employee_id": req["employee_id"]})
    emp_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip() if emp else req["employee_id"]
    dispatch_event(
        event_type=HREventType.LEAVE_REJECTED,
        entity_type="leave_request",
        entity_id=leave_id,
        target_employee_id=req["employee_id"],
        payload={
            "employee_id": req["employee_id"],
            "employee_name": emp_name,
            "leave_type": req["leave_type"],
            "days_count": req["days_count"],
            "start_date": req["start_date"],
            "reason": reason,
            "approver_id": approver_id
        },
        dedup_key=f"LEAVE_REJ_{leave_id}"
    )

    return db.leave_requests.find_one({"leave_id": leave_id}, {"_id": 0})
