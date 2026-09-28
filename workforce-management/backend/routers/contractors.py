"""
Contractor & Vendor Workforce Management Router
-----------------------------------------------
Handles external vendors, contract durations, contractor timesheets,
hourly billing, and non-employee access boundaries.
"""

from typing import List, Optional
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.auth.dependencies import get_current_user, require_role
from backend.schemas.contractor import (
    ContractorResponse, ContractorCreate, ContractorTimesheetCreate, ContractorTimesheetResponse
)

router = APIRouter(prefix="/contractors", tags=["Contractor & Vendor Workforce"])

INITIAL_CONTRACTORS = [
    {
        "contractor_id": "CON001",
        "first_name": "Arjun",
        "last_name": "Mehta",
        "email": "arjun.m@apexcloud.com",
        "vendor_org": "Apex Cloud Solutions",
        "contract_type": "Time & Materials",
        "start_date": "2026-01-15",
        "end_date": "2026-12-31",
        "hourly_billing_rate": 65.0,
        "currency": "USD",
        "assigned_location_id": "LOC01",
        "assigned_project_id": "PRJ01",
        "manager_id": "EMP003",
        "status": "Active"
    },
    {
        "contractor_id": "CON002",
        "first_name": "Sarah",
        "last_name": "Jenkins",
        "email": "s.jenkins@cyberguard.io",
        "vendor_org": "CyberGuard Systems",
        "contract_type": "Fixed Term",
        "start_date": "2026-02-01",
        "end_date": "2026-08-31",
        "hourly_billing_rate": 80.0,
        "currency": "USD",
        "assigned_location_id": "LOC02",
        "assigned_project_id": "PRJ02",
        "manager_id": "EMP003",
        "status": "Active"
    },
    {
        "contractor_id": "CON003",
        "first_name": "Vikram",
        "last_name": "Rathore",
        "email": "vikram.r@datasync.in",
        "vendor_org": "DataSync Analytics",
        "contract_type": "SOW",
        "start_date": "2026-03-01",
        "end_date": "2026-09-30",
        "hourly_billing_rate": 55.0,
        "currency": "USD",
        "assigned_location_id": "LOC01",
        "assigned_project_id": "PRJ03",
        "manager_id": "EMP005",
        "status": "Active"
    }
]

def ensure_seed_contractors(db):
    if db.contractors.count_documents({}) == 0:
        db.contractors.insert_many(INITIAL_CONTRACTORS)

@router.get("", response_model=List[ContractorResponse], summary="List contractors and vendor personnel")
async def list_contractors(
    vendor_org: Optional[str] = None,
    status: Optional[str] = None,
    project_id: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    ensure_seed_contractors(db)
    
    query = {}
    if vendor_org:
        query["vendor_org"] = vendor_org
    if status:
        query["status"] = status
    if project_id:
        query["assigned_project_id"] = project_id
        
    contractors = list(db.contractors.find(query, {"_id": 0}))
    for c in contractors:
        cid = c["contractor_id"]
        timesheets = list(db.contractor_timesheets.find({"contractor_id": cid}))
        c["total_billed_hours"] = sum(t.get("hours_worked", 0.0) for t in timesheets)
        c["active_timesheets_count"] = len(timesheets)
        
    return contractors

@router.get("/{contractor_id}", response_model=ContractorResponse, summary="Get contractor details")
async def get_contractor(contractor_id: str, current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    ensure_seed_contractors(db)
    
    c = db.contractors.find_one({"contractor_id": contractor_id}, {"_id": 0})
    if not c:
        raise HTTPException(status_code=404, detail=f"Contractor '{contractor_id}' not found.")
        
    timesheets = list(db.contractor_timesheets.find({"contractor_id": contractor_id}))
    c["total_billed_hours"] = sum(t.get("hours_worked", 0.0) for t in timesheets)
    c["active_timesheets_count"] = len(timesheets)
    return c

@router.post("", response_model=ContractorResponse, status_code=status.HTTP_201_CREATED, summary="Onboard a new vendor contractor (HR/Admin only)")
async def create_contractor(payload: ContractorCreate, current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    ensure_seed_contractors(db)
    
    # Generate ID if not provided
    if not payload.contractor_id:
        count = db.contractors.count_documents({}) + 1
        payload.contractor_id = f"CON{str(count).zfill(3)}"
        
    if db.contractors.find_one({"contractor_id": payload.contractor_id}):
        raise HTTPException(status_code=409, detail=f"Contractor '{payload.contractor_id}' already exists.")
        
    doc = payload.dict()
    db.contractors.insert_one(doc)
    
    # Audit log
    db.audit_logs.insert_one({
        "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor_user_id": current_user.get("user_id"),
        "actor_role": current_user.get("role"),
        "action": "CREATE_CONTRACTOR",
        "resource_type": "contractor",
        "resource_id": payload.contractor_id,
        "status": "SUCCESS",
        "details": {"vendor_org": payload.vendor_org, "assigned_project": payload.assigned_project_id}
    })
    
    return db.contractors.find_one({"contractor_id": payload.contractor_id}, {"_id": 0})

@router.get("/{contractor_id}/timesheets", response_model=List[ContractorTimesheetResponse], summary="Get contractor billing timesheets")
async def get_contractor_timesheets(contractor_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    ensure_seed_contractors(db)
    return list(db.contractor_timesheets.find({"contractor_id": contractor_id}, {"_id": 0}))

@router.post("/{contractor_id}/timesheets", response_model=ContractorTimesheetResponse, status_code=status.HTTP_201_CREATED, summary="Submit contractor weekly billing timesheet")
async def submit_contractor_timesheet(
    contractor_id: str,
    payload: ContractorTimesheetCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    ensure_seed_contractors(db)
    
    c = db.contractors.find_one({"contractor_id": contractor_id})
    if not c:
        raise HTTPException(status_code=404, detail=f"Contractor '{contractor_id}' not found.")
        
    rate = c.get("hourly_billing_rate", 0.0)
    total_amount = round(payload.hours_worked * rate, 2)
    
    timesheet_id = f"TS_CON_{uuid.uuid4().hex[:8].upper()}"
    ts_doc = {
        "timesheet_id": timesheet_id,
        "contractor_id": contractor_id,
        "vendor_org": c.get("vendor_org"),
        "week_start_date": payload.week_start_date,
        "hours_worked": payload.hours_worked,
        "hourly_rate": rate,
        "total_amount": total_amount,
        "currency": c.get("currency", "USD"),
        "task_description": payload.task_description,
        "status": "Submitted",
        "approved_by": None,
        "approval_date": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    db.contractor_timesheets.insert_one(ts_doc)
    return db.contractor_timesheets.find_one({"timesheet_id": timesheet_id}, {"_id": 0})

@router.put("/timesheets/{timesheet_id}/approve", response_model=ContractorTimesheetResponse, summary="Approve contractor billing timesheet (Manager/HR/Admin)")
async def approve_contractor_timesheet(
    timesheet_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    ts = db.contractor_timesheets.find_one({"timesheet_id": timesheet_id})
    if not ts:
        raise HTTPException(status_code=404, detail=f"Timesheet '{timesheet_id}' not found.")
        
    now_iso = datetime.now(timezone.utc).isoformat()
    db.contractor_timesheets.update_one(
        {"timesheet_id": timesheet_id},
        {"$set": {
            "status": "Approved",
            "approved_by": current_user.get("user_id"),
            "approval_date": now_iso
        }}
    )
    
    # Audit log
    db.audit_logs.insert_one({
        "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
        "timestamp": now_iso,
        "actor_user_id": current_user.get("user_id"),
        "actor_role": current_user.get("role"),
        "action": "APPROVE_CONTRACTOR_TIMESHEET",
        "resource_type": "contractor_timesheet",
        "resource_id": timesheet_id,
        "status": "SUCCESS",
        "details": {"contractor_id": ts["contractor_id"], "amount": ts["total_amount"]}
    })
    
    return db.contractor_timesheets.find_one({"timesheet_id": timesheet_id}, {"_id": 0})
