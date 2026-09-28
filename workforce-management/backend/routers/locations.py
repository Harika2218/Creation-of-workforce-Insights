"""
Multi-Location Workforce Management Router
------------------------------------------
Handles enterprise locations, regional campuses, location-specific geofencing,
and location-filtered workforce allocations.
"""

from typing import List, Optional
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.auth.dependencies import get_current_user, require_role
from backend.schemas.location import (
    LocationResponse, LocationCreate, LocationGeofenceUpdate, LocationDetailResponse
)

router = APIRouter(prefix="/locations", tags=["Multi-Location Workforce"])

@router.get("", response_model=List[LocationResponse], summary="List enterprise locations and campuses")
async def list_locations(current_user: dict = Depends(get_current_user)):
    db = get_db()
    locs = list(db.locations.find({}, {"_id": 0}))
    
    # Enrich with employee counts and active shifts
    for loc in locs:
        loc_id = loc["location_id"]
        loc["employee_count"] = db.employees.count_documents({"location_id": loc_id, "employment_status": "Active"})
        loc["active_shifts_count"] = db.shifts.count_documents({})
    
    return locs

@router.get("/{location_id}", response_model=LocationDetailResponse, summary="Get location details with departments & holidays")
async def get_location_details(location_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    loc = db.locations.find_one({"location_id": location_id}, {"_id": 0})
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location '{location_id}' not found."
        )
    
    # Aggregate departments and holidays
    depts = db.employees.distinct("department_id", {"location_id": location_id})
    emp_count = db.employees.count_documents({"location_id": location_id, "employment_status": "Active"})
    holidays_count = db.holidays.count_documents({"$or": [{"location_id": location_id}, {"location_id": None}]})
    
    loc["departments"] = depts
    loc["employee_count"] = emp_count
    loc["active_shifts_count"] = db.shifts.count_documents({})
    loc["holidays_count"] = holidays_count
    return loc

@router.get("/{location_id}/employees", summary="Get employees stationed at location")
async def get_location_employees(
    location_id: str,
    department_id: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    loc = db.locations.find_one({"location_id": location_id})
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found.")
    
    query = {"location_id": location_id}
    if department_id:
        query["department_id"] = department_id
        
    emps = list(db.employees.find(
        query,
        {"_id": 0, "employee_id": 1, "first_name": 1, "last_name": 1, "email": 1, "department_id": 1, "job_title": 1, "employment_status": 1}
    ).limit(limit))
    
    return {
        "location_id": location_id,
        "location_name": loc["name"],
        "count": len(emps),
        "employees": emps
    }

@router.get("/{location_id}/holidays", summary="Get holiday schedule applicable to location")
async def get_location_holidays(location_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    loc = db.locations.find_one({"location_id": location_id})
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found.")
    
    holidays = list(db.holidays.find(
        {"$or": [{"location_id": location_id}, {"location_id": None}, {"location_id": {"$exists": False}}]},
        {"_id": 0}
    ).sort("holiday_date", 1))
    
    return {
        "location_id": location_id,
        "location_name": loc["name"],
        "holidays": holidays
    }

@router.put("/{location_id}/geofence", response_model=LocationResponse, summary="Update location geofence boundary (HR/Admin only)")
async def update_location_geofence(
    location_id: str,
    payload: LocationGeofenceUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    loc = db.locations.find_one({"location_id": location_id})
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found.")
    
    update_data = {
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "geofence_radius_meters": payload.geofence_radius_meters,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    db.locations.update_one({"location_id": location_id}, {"$set": update_data})
    
    # Audit log
    db.audit_logs.insert_one({
        "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor_user_id": current_user.get("user_id"),
        "actor_role": current_user.get("role"),
        "action": "UPDATE_LOCATION_GEOFENCE",
        "resource_type": "location",
        "resource_id": location_id,
        "status": "SUCCESS",
        "details": update_data
    })
    
    updated_loc = db.locations.find_one({"location_id": location_id}, {"_id": 0})
    updated_loc["employee_count"] = db.employees.count_documents({"location_id": location_id, "employment_status": "Active"})
    updated_loc["active_shifts_count"] = db.shifts.count_documents({})
    return updated_loc
