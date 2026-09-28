"""
Shift Management Router
-----------------------
Shift schedules, roster allocations, and shift swap workflows.
"""

from typing import List, Optional
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.shifts import (
    ShiftCreate, ShiftResponse, ShiftAssignRequest, ShiftSwapRequestCreate, ShiftSwapResponse
)
from backend.schemas.common import MessageResponse
from backend.auth.dependencies import get_current_user, require_role
from backend.events.events import HREventType
from backend.events.dispatcher import dispatch_event

router = APIRouter(prefix="/shifts", tags=["Shifts"])

@router.get("", response_model=List[ShiftResponse], summary="List all configured shifts")
async def list_shifts(current_user: dict = Depends(get_current_user)):
    db = get_db()
    return list(db.shifts.find({}, {"_id": 0}).sort("shift_id", 1))

@router.get("/{shift_id}", response_model=ShiftResponse, summary="Get shift by ID")
async def get_shift(shift_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    s = db.shifts.find_one({"shift_id": shift_id}, {"_id": 0})
    if not s:
        raise HTTPException(status_code=404, detail=f"Shift '{shift_id}' not found.")
    return s

@router.post("", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED, summary="Create shift (HR/Admin only)")
async def create_shift(payload: ShiftCreate, current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    if db.shifts.find_one({"shift_id": payload.shift_id}):
        raise HTTPException(status_code=409, detail=f"Shift ID '{payload.shift_id}' already exists.")
    doc = payload.model_dump()
    db.shifts.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.get("/employee/{employee_id}", summary="Get shift assignment for an employee")
async def get_employee_shift(employee_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    assignment = db.employee_shifts.find_one({"employee_id": employee_id}, {"_id": 0})
    if not assignment:
        raise HTTPException(status_code=404, detail=f"No shift assignment for '{employee_id}'.")
    shift = db.shifts.find_one({"shift_id": assignment["shift_id"]}, {"_id": 0})
    return {
        "employee_id": employee_id,
        "schedule": assignment,
        "shift_details": shift
    }

@router.post("/assign", response_model=MessageResponse, summary="Assign shift to employee")
async def assign_shift(payload: ShiftAssignRequest, current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    if not db.employees.find_one({"employee_id": payload.employee_id}):
        raise HTTPException(status_code=404, detail=f"Employee '{payload.employee_id}' not found.")
    if not db.shifts.find_one({"shift_id": payload.shift_id}):
        raise HTTPException(status_code=404, detail=f"Shift '{payload.shift_id}' not found.")

    doc = {
        "schedule_id": f"SCH_{payload.employee_id}",
        "employee_id": payload.employee_id,
        "shift_id": payload.shift_id,
        "effective_from": payload.effective_from,
        "effective_to": payload.effective_to
    }
    db.employee_shifts.replace_one({"employee_id": payload.employee_id}, doc, upsert=True)

    # Phase 7: Dispatch Shift Assignment Event
    shift = db.shifts.find_one({"shift_id": payload.shift_id})
    emp = db.employees.find_one({"employee_id": payload.employee_id})
    emp_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip() if emp else payload.employee_id
    dispatch_event(
        event_type=HREventType.SHIFT_ASSIGNED,
        entity_type="shift",
        entity_id=payload.shift_id,
        target_employee_id=payload.employee_id,
        payload={
            "employee_id": payload.employee_id,
            "employee_name": emp_name,
            "shift_name": shift.get("shift_name", payload.shift_id) if shift else payload.shift_id,
            "effective_date": payload.effective_from or "immediately"
        },
        dedup_key=f"SHIFT_ASSIGN_{payload.employee_id}_{payload.shift_id}"
    )

    return {"message": f"Shift '{payload.shift_id}' successfully assigned to employee '{payload.employee_id}'."}

@router.post("/swap-request", response_model=ShiftSwapResponse, status_code=status.HTTP_201_CREATED, summary="Submit shift swap request")
async def request_shift_swap(payload: ShiftSwapRequestCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    swap_id = f"SWP_{uuid.uuid4().hex[:6].upper()}"
    swap_doc = payload.model_dump()
    swap_doc.update({
        "swap_id": swap_id,
        "status": "Pending",
        "approved_by": None
    })
    db.shift_swap_requests.insert_one(swap_doc)
    swap_doc.pop("_id", None)

    # Phase 7: Dispatch Shift Swap Requested Event
    req_emp = db.employees.find_one({"employee_id": payload.requester_id})
    req_name = f"{req_emp.get('first_name', '')} {req_emp.get('last_name', '')}".strip() if req_emp else payload.requester_id
    dispatch_event(
        event_type=HREventType.SHIFT_SWAP_REQUESTED,
        entity_type="shift_swap",
        entity_id=swap_id,
        target_employee_id=payload.target_employee_id,
        payload={
            "swap_id": swap_id,
            "requester_id": payload.requester_id,
            "requester_name": req_name,
            "target_employee_id": payload.target_employee_id,
            "shift_name": payload.shift_id
        },
        dedup_key=f"SWAP_REQ_{swap_id}"
    )

    return swap_doc

@router.get("/swap-requests", response_model=List[ShiftSwapResponse], summary="List shift swap requests")
async def list_swap_requests(
    status_val: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    query = {}
    if current_user.get("role") == "EMPLOYEE":
        query["$or"] = [
            {"requester_id": current_user.get("employee_id")},
            {"target_employee_id": current_user.get("employee_id")}
        ]
    if status_val:
        query["status"] = status_val
    return list(db.shift_swap_requests.find(query, {"_id": 0}))

@router.put("/swap-requests/{swap_id}", response_model=ShiftSwapResponse, summary="Approve/Reject shift swap request")
async def update_swap_request(
    swap_id: str,
    action: str, # Approved or Rejected
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    existing = db.shift_swap_requests.find_one({"swap_id": swap_id})
    if not existing:
        raise HTTPException(status_code=404, detail=f"Swap request '{swap_id}' not found.")

    if action not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Action must be 'Approved' or 'Rejected'.")

    db.shift_swap_requests.update_one(
        {"swap_id": swap_id},
        {"$set": {"status": action, "approved_by": current_user.get("employee_id")}}
    )

    # If approved, update shift allocations
    if action == "Approved":
        db.employee_shifts.update_one(
            {"employee_id": existing["requester_id"]},
            {"$set": {"shift_id": existing["target_shift_id"]}}
        )
        db.employee_shifts.update_one(
            {"employee_id": existing["target_employee_id"]},
            {"$set": {"shift_id": existing["shift_id"]}}
        )
        dispatch_event(
            event_type=HREventType.SHIFT_SWAP_APPROVED,
            entity_type="shift_swap",
            entity_id=swap_id,
            target_employee_id=existing["requester_id"],
            payload={"swap_id": swap_id},
            dedup_key=f"SWAP_APP_{swap_id}"
        )
    else:
        dispatch_event(
            event_type=HREventType.SHIFT_SWAP_REJECTED,
            entity_type="shift_swap",
            entity_id=swap_id,
            target_employee_id=existing["requester_id"],
            payload={"swap_id": swap_id},
            dedup_key=f"SWAP_REJ_{swap_id}"
        )

    return db.shift_swap_requests.find_one({"swap_id": swap_id}, {"_id": 0})
