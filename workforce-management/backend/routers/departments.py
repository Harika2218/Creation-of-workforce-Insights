"""
Department Router
-----------------
CRUD operations for company departments.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.departments import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from backend.schemas.common import MessageResponse
from backend.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("", response_model=List[DepartmentResponse], summary="List all departments with employee counts")
async def list_departments(current_user: dict = Depends(get_current_user)):
    db = get_db()
    departments = list(db.departments.find({}, {"_id": 0}).sort("department_id", 1))

    # Enrich with employee counts
    for dept in departments:
        dept["employee_count"] = db.employees.count_documents({
            "department_id": dept["department_id"],
            "employment_status": {"$ne": "Deactivated"}
        })

    return departments

@router.get("/{department_id}", response_model=DepartmentResponse, summary="Get department by ID")
async def get_department(department_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    dept = db.departments.find_one({"department_id": department_id}, {"_id": 0})
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{department_id}' not found."
        )
    dept["employee_count"] = db.employees.count_documents({"department_id": department_id})
    return dept

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, summary="Create new department (Admin/HR only)")
async def create_department(
    payload: DepartmentCreate,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    if db.departments.find_one({"department_id": payload.department_id}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department ID '{payload.department_id}' already exists."
        )
    if db.departments.find_one({"code": payload.code.upper()}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department code '{payload.code}' already exists."
        )

    doc = payload.model_dump()
    doc["code"] = doc["code"].upper()
    db.departments.insert_one(doc)
    doc.pop("_id", None)
    doc["employee_count"] = 0
    return doc

@router.put("/{department_id}", response_model=DepartmentResponse, summary="Update department (Admin/HR only)")
async def update_department(
    department_id: str,
    payload: DepartmentUpdate,
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    existing = db.departments.find_one({"department_id": department_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{department_id}' not found."
        )

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if updates:
        db.departments.update_one({"department_id": department_id}, {"$set": updates})

    updated = db.departments.find_one({"department_id": department_id}, {"_id": 0})
    updated["employee_count"] = db.employees.count_documents({"department_id": department_id})
    return updated
