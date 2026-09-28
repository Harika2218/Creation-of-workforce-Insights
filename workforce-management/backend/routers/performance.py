"""
Performance Appraisals & Reviews Router
"""

from typing import List, Optional
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.performance import PerformanceCreate, PerformanceResponse
from backend.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/performance", tags=["Performance"])

@router.get("", response_model=List[PerformanceResponse], summary="List performance reviews")
async def list_performance(
    department_id: Optional[str] = None,
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

    reviews = list(db.performance_reviews.find(query, {"_id": 0}))
    return reviews

@router.get("/{employee_id}", response_model=List[PerformanceResponse], summary="Get performance reviews for an employee")
async def get_employee_performance(employee_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot view another employee's performance review.")

    db = get_db()
    return list(db.performance_reviews.find({"employee_id": employee_id}, {"_id": 0}))

@router.post("", response_model=PerformanceResponse, status_code=status.HTTP_201_CREATED, summary="Create performance appraisal (Manager/HR/Admin only)")
async def create_performance_review(
    payload: PerformanceCreate,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    if not db.employees.find_one({"employee_id": payload.employee_id}):
        raise HTTPException(status_code=404, detail=f"Employee '{payload.employee_id}' not found.")

    rev_id = f"REV_{uuid.uuid4().hex[:6].upper()}"
    reviewer_id = current_user.get("employee_id") or "ADMIN"
    doc = payload.model_dump()
    doc.update({
        "review_id": rev_id,
        "reviewer_id": reviewer_id
    })
    db.performance_reviews.insert_one(doc)
    doc.pop("_id", None)
    return doc
