"""
Employee Management Router
--------------------------
Handles employee onboarding, directory search, pagination, updates, and soft deactivation.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.schemas.common import PaginatedResponse, MessageResponse
from backend.schemas.employees import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeProfileResponse
)
from backend.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("", response_model=PaginatedResponse[EmployeeResponse], summary="List and filter employees with pagination")
async def list_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    employment_status: Optional[str] = Query(None, description="Filter by status (Active, On Notice, Deactivated)"),
    search: Optional[str] = Query(None, description="Search by name, ID, or email"),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    query = {}

    if department_id:
        query["department_id"] = department_id
    if role:
        query["role"] = role
    if location_id:
        query["location_id"] = location_id
    if employment_status:
        query["employment_status"] = employment_status
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"employee_id": search_regex},
            {"first_name": search_regex},
            {"last_name": search_regex},
            {"email": search_regex},
            {"designation": search_regex}
        ]

    total = db.employees.count_documents(query)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    skip = (page - 1) * page_size

    employees = list(db.employees.find(query, {"_id": 0}).sort("employee_id", 1).skip(skip).limit(page_size))

    return {
        "data": employees,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/{employee_id}", response_model=EmployeeResponse, summary="Get single employee by ID")
async def get_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    emp = db.employees.find_one({"employee_id": employee_id}, {"_id": 0})
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found."
        )
    return emp

@router.get("/{employee_id}/profile", response_model=EmployeeProfileResponse, summary="Get full employee profile with relations")
async def get_employee_profile(employee_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    emp = db.employees.find_one({"employee_id": employee_id}, {"_id": 0})
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found."
        )

    # Department
    dept = db.departments.find_one({"department_id": emp["department_id"]}, {"name": 1})
    dept_name = dept["name"] if dept else "Unknown"

    # Location
    loc = db.locations.find_one({"location_id": emp["location_id"]}, {"name": 1, "city": 1})
    loc_name = f"{loc['name']} ({loc['city']})" if loc else "Unknown"

    # Manager
    mgr_name = None
    if emp.get("manager_id"):
        mgr = db.employees.find_one({"employee_id": emp["manager_id"]}, {"first_name": 1, "last_name": 1})
        if mgr:
            mgr_name = f"{mgr['first_name']} {mgr['last_name']}"

    # Skills
    skills = list(db.employee_skills.find({"employee_id": employee_id}, {"_id": 0}))

    # Leave balances
    balances = list(db.leave_balances.find({"employee_id": employee_id}, {"_id": 0}))

    profile = dict(emp)
    profile["department_name"] = dept_name
    profile["location_name"] = loc_name
    profile["manager_name"] = mgr_name
    profile["skills"] = skills
    profile["leave_balances"] = balances

    return profile

@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, summary="Onboard new employee (HR/Admin only)")
async def create_employee(
    payload: EmployeeCreate,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()

    # Determine or validate employee_id
    if not payload.employee_id:
        count = db.employees.count_documents({})
        new_id = f"EMP{count + 1:03d}"
    else:
        new_id = payload.employee_id

    # Check for duplicate employee_id or email
    if db.employees.find_one({"employee_id": new_id}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee ID '{new_id}' already exists."
        )
    if db.employees.find_one({"email": payload.email.lower()}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email address '{payload.email}' is already registered."
        )

    # Validate referenced department
    if not db.departments.find_one({"department_id": payload.department_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department '{payload.department_id}' does not exist."
        )

    # Validate referenced location
    if not db.locations.find_one({"location_id": payload.location_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location '{payload.location_id}' does not exist."
        )

    # Validate referenced manager (if provided)
    if payload.manager_id and not db.employees.find_one({"employee_id": payload.manager_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Manager '{payload.manager_id}' does not exist in employee directory."
        )

    emp_doc = payload.model_dump()
    emp_doc["employee_id"] = new_id
    emp_doc["email"] = payload.email.lower()

    db.employees.insert_one(emp_doc)
    emp_doc.pop("_id", None)
    return emp_doc

@router.put("/{employee_id}", response_model=EmployeeResponse, summary="Update employee profile (HR/Admin only)")
async def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    existing = db.employees.find_one({"employee_id": employee_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found."
        )

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if updates:
        db.employees.update_one({"employee_id": employee_id}, {"$set": updates})

    updated = db.employees.find_one({"employee_id": employee_id}, {"_id": 0})
    return updated

@router.delete("/{employee_id}", response_model=MessageResponse, summary="Soft-deactivate employee (HR/Admin only)")
async def deactivate_employee(
    employee_id: str,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    existing = db.employees.find_one({"employee_id": employee_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found."
        )

    db.employees.update_one({"employee_id": employee_id}, {"$set": {"employment_status": "Deactivated"}})
    return {
        "message": f"Employee '{employee_id}' has been soft-deactivated successfully.",
        "success": True,
        "details": {"employee_id": employee_id, "new_status": "Deactivated"}
    }
