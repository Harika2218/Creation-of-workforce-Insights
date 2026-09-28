"""
Reports & Analytics Router
--------------------------
Generates workforce reports for attendance, overtime, leaves, payroll costs, and department performance.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from database.mongodb import get_db
from backend.auth.dependencies import require_role

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/attendance", summary="Attendance summary report across date range")
async def report_attendance(
    start_date: str = Query("2026-03-01"),
    end_date: str = Query("2026-03-20"),
    department_id: Optional[str] = None,
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    match = {"date": {"$gte": start_date, "$lte": end_date}}
    if department_id:
        emp_ids = db.employees.distinct("employee_id", {"department_id": department_id})
        match["employee_id"] = {"$in": emp_ids}

    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": "$attendance_status",
            "count": {"$sum": 1},
            "total_overtime": {"$sum": "$overtime_hours"}
        }}
    ]
    results = list(db.attendance.aggregate(pipeline))
    return {
        "start_date": start_date,
        "end_date": end_date,
        "department_id": department_id or "ALL",
        "breakdown": results
    }

@router.get("/overtime", summary="Overtime report by department and employee")
async def report_overtime(
    month: str = Query("2026-03"),
    current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))
):
    db = get_db()
    pipeline = [
        {"$match": {"date": {"$regex": f"^{month}"}, "overtime_hours": {"$gt": 0}}},
        {"$group": {
            "_id": "$employee_id",
            "total_overtime_hours": {"$sum": "$overtime_hours"},
            "sessions": {"$sum": 1}
        }},
        {"$sort": {"total_overtime_hours": -1}},
        {"$limit": 20}
    ]
    top_ot = list(db.attendance.aggregate(pipeline))
    return {
        "month": month,
        "top_overtime_employees": top_ot
    }

@router.get("/leave", summary="Leave utilization report by category")
async def report_leave(current_user: dict = Depends(require_role(["ADMIN", "HR", "MANAGER"]))):
    db = get_db()
    pipeline = [
        {"$group": {
            "_id": "$leave_type",
            "total_allocated": {"$sum": "$allocated_days"},
            "total_used": {"$sum": "$used_days"},
            "total_remaining": {"$sum": "$remaining_days"}
        }}
    ]
    return {
        "report": "Company-wide Leave Utilization",
        "data": list(db.leave_balances.aggregate(pipeline))
    }

@router.get("/payroll", summary="Workforce compensation & payroll cost trends")
async def report_payroll(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    pipeline = [
        {"$group": {
            "_id": "$month",
            "total_gross": {"$sum": "$gross_salary"},
            "total_net": {"$sum": "$net_salary"},
            "total_taxes": {"$sum": "$deductions"},
            "headcount": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    return {
        "trend": "6-Month Historical Payroll Disbursement",
        "months": list(db.payroll_records.aggregate(pipeline))
    }

@router.get("/department-performance", summary="Average KPI and productivity by department")
async def report_dept_performance(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    # Join employees with performance_reviews
    pipeline = [
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "emp"
            }
        },
        {"$unwind": "$emp"},
        {
            "$group": {
                "_id": "$emp.department_id",
                "avg_kpi": {"$avg": "$kpi_score"},
                "avg_productivity": {"$avg": "$productivity_score"},
                "avg_goal_completion": {"$avg": "$goal_completion"},
                "employee_count": {"$sum": 1}
            }
        },
        {"$sort": {"avg_productivity": -1}}
    ]
    return {
        "report": "Department Performance Benchmarks",
        "departments": list(db.performance_reviews.aggregate(pipeline))
    }

@router.get("/audit-logs", summary="List system audit logs (Admin/HR only)")
async def report_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_role(["ADMIN", "HR"]))
):
    db = get_db()
    query = {}
    if action:
        query["action"] = action
    if user_id:
        query["user_id"] = user_id

    total = db.audit_logs.count_documents(query)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    skip = (page - 1) * page_size

    logs = list(db.audit_logs.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(page_size))
    return {
        "data": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

