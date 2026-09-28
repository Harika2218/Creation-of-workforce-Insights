"""
Payroll Router
--------------
Secure salary disbursements, monthly payroll records, and aggregated payroll summaries.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.schemas.payroll import PayrollResponse, PayrollSummaryResponse
from backend.schemas.common import PaginatedResponse
from backend.auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/payroll", tags=["Payroll"])

@router.get("", response_model=PaginatedResponse[PayrollResponse], summary="List payroll records with pagination & filters")
async def list_payroll(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[str] = Query(None),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    query = {}

    user_role = current_user.get("role", "EMPLOYEE")
    # Strict RBAC: EMPLOYEE can only view their own payroll records
    if user_role == "EMPLOYEE":
        query["employee_id"] = current_user.get("employee_id")
    elif employee_id:
        query["employee_id"] = employee_id

    if month:
        query["month"] = month

    total = db.payroll_records.count_documents(query)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    skip = (page - 1) * page_size

    records = list(db.payroll_records.find(query, {"_id": 0}).sort("month", -1).skip(skip).limit(page_size))

    return {
        "data": records,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/summary", response_model=PayrollSummaryResponse, summary="Get monthly payroll cost summary (HR/Admin only)")
async def payroll_summary(
    month: str = Query("2026-03", description="Month in YYYY-MM format"),
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    pipeline = [
        {"$match": {"month": month}},
        {"$group": {
            "_id": "$month",
            "total_count": {"$sum": 1},
            "total_base": {"$sum": "$base_salary"},
            "total_ot": {"$sum": "$overtime_pay"},
            "total_bonuses": {"$sum": {"$add": ["$incentives", "$bonuses"]}},
            "total_gross": {"$sum": "$gross_salary"},
            "total_deductions": {"$sum": "$deductions"},
            "total_net": {"$sum": "$net_salary"}
        }}
    ]
    res = list(db.payroll_records.aggregate(pipeline))
    if not res:
        raise HTTPException(status_code=404, detail=f"No payroll data found for month '{month}'.")

    d = res[0]
    return {
        "month": month,
        "total_employees_paid": d["total_count"],
        "total_base_payroll": round(d["total_base"], 2),
        "total_overtime_paid": round(d["total_ot"], 2),
        "total_bonuses_incentives": round(d["total_bonuses"], 2),
        "total_gross_disbursement": round(d["total_gross"], 2),
        "total_deductions": round(d["total_deductions"], 2),
        "total_net_disbursement": round(d["total_net"], 2)
    }

@router.get("/{payroll_id}", response_model=PayrollResponse, summary="Get specific payslip record")
async def get_payroll_record(payroll_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    rec = db.payroll_records.find_one({"payroll_id": payroll_id}, {"_id": 0})
    if not rec:
        raise HTTPException(status_code=404, detail=f"Payroll record '{payroll_id}' not found.")

    # RBAC security
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != rec["employee_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot view another employee's payslip.")

    return rec

@router.get("/employee/{employee_id}", response_model=List[PayrollResponse], summary="Get all payslips for an employee")
async def get_employee_payrolls(employee_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") == "EMPLOYEE" and current_user.get("employee_id") != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot view another employee's payslips.")

    db = get_db()
    return list(db.payroll_records.find({"employee_id": employee_id}, {"_id": 0}).sort("month", -1))
