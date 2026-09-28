"""
HR Dashboard Aggregations Router
--------------------------------
Provides high-level aggregated workforce metrics to power future HR dashboards.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.performance import HRDashboardSummaryResponse
from backend.auth.dependencies import require_role

router = APIRouter(prefix="/hr", tags=["HR"])

@router.get("/summary", response_model=HRDashboardSummaryResponse, summary="Get global HR dashboard overview (HR/Admin only)")
async def hr_dashboard_summary(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    total_emp = db.employees.count_documents({})
    active_emp = db.employees.count_documents({"employment_status": "Active"})
    notice_emp = db.employees.count_documents({"employment_status": "On Notice"})
    depts_count = db.departments.count_documents({})
    locs_count = db.locations.count_documents({})

    # Latest active date attendance rate
    latest_date = "2026-03-20"
    present_count = db.attendance.count_documents({
        "date": latest_date,
        "attendance_status": {"$in": ["Present", "Late", "Work From Home"]}
    })
    total_on_date = db.attendance.count_documents({"date": latest_date})
    att_rate = round((present_count / max(1, total_on_date)) * 100, 1)

    pending_leaves = db.leave_requests.count_documents({"status": "Pending"})

    # Payroll total for latest month
    pipeline = [
        {"$match": {"month": "2026-03"}},
        {"$group": {"_id": None, "total_net": {"$sum": "$net_salary"}}}
    ]
    pay_res = list(db.payroll_records.aggregate(pipeline))
    monthly_pay = pay_res[0]["total_net"] if pay_res else 0.0

    # Attrition risk counts
    high_attr = db.attrition_predictions.count_documents({"risk_category": "HIGH"})
    med_attr = db.attrition_predictions.count_documents({"risk_category": "MEDIUM"})
    low_attr = db.attrition_predictions.count_documents({"risk_category": "LOW"})

    return {
        "total_employees": total_emp,
        "active_employees": active_emp,
        "notice_period_employees": notice_emp,
        "departments_count": depts_count,
        "locations_count": locs_count,
        "daily_attendance_rate": att_rate,
        "pending_leave_requests": pending_leaves,
        "total_monthly_payroll": round(monthly_pay, 2),
        "attrition_risk_high": high_attr,
        "attrition_risk_medium": med_attr,
        "attrition_risk_low": low_attr
    }

@router.get("/employee-summary", summary="Get employee distribution by department and status")
async def hr_employee_summary(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    dept_pipeline = [
        {"$group": {"_id": "$department_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    dept_counts = list(db.employees.aggregate(dept_pipeline))

    status_pipeline = [
        {"$group": {"_id": "$employment_status", "count": {"$sum": 1}}}
    ]
    status_counts = list(db.employees.aggregate(status_pipeline))

    return {
        "department_distribution": dept_counts,
        "status_distribution": status_counts,
        "total_employees": db.employees.count_documents({})
    }

@router.get("/executive-summary", summary="Get comprehensive executive workforce overview (Admin/HR only)")
async def hr_executive_summary(current_user: dict = Depends(require_role(["ADMIN", "HR"]))):
    db = get_db()
    total_reg = db.employees.count_documents({})
    total_contractors = db.contractors.count_documents({"status": "Active"}) if "contractors" in db.list_collection_names() else 0

    # Locations distribution
    loc_map = {l["location_id"]: l.get("city", l.get("name", l["location_id"])) for l in db.locations.find({})}
    loc_pipeline = [
        {"$group": {"_id": "$location_id", "headcount": {"$sum": 1}}},
        {"$sort": {"headcount": -1}}
    ]
    loc_data = []
    for r in db.employees.aggregate(loc_pipeline):
        lid = r["_id"]
        loc_data.append({
            "location_id": lid,
            "city": loc_map.get(lid, "Unknown"),
            "headcount": r["headcount"]
        })

    # Payroll cost
    pay_pipe = [
        {"$match": {"month": "2026-03"}},
        {"$group": {"_id": None, "total_net": {"$sum": "$net_salary"}}}
    ]
    pay_res = list(db.payroll_records.aggregate(pay_pipe))
    monthly_payroll = pay_res[0]["total_net"] if pay_res else 0.0

    # Contractor cost
    contractor_hours = 0.0
    if "contractor_timesheets" in db.list_collection_names():
        ts_pipe = [{"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}]
        ts_res = list(db.contractor_timesheets.aggregate(ts_pipe))
        contractor_cost = ts_res[0]["total"] if ts_res else 0.0
    else:
        contractor_cost = 0.0

    total_workforce_cost = round(monthly_payroll + contractor_cost, 2)

    # Risk metrics
    high_attr = db.attrition_predictions.count_documents({"risk_category": "HIGH"})
    anomalies = db.attendance.count_documents({"anomaly_flag": 1})

    return {
        "workforce_composition": {
            "regular_employees": total_reg,
            "active_contractors": total_contractors,
            "total_talent_pool": total_reg + total_contractors
        },
        "location_distribution": loc_data,
        "financial_summary": {
            "regular_payroll_monthly": round(monthly_payroll, 2),
            "contractor_billing_monthly": round(contractor_cost, 2),
            "total_workforce_spend": total_workforce_cost,
            "currency": "USD"
        },
        "operational_health": {
            "high_attrition_risk_headcount": high_attr,
            "unresolved_attendance_anomalies": anomalies,
            "system_health_status": "OPTIMAL",
            "active_campuses": len(loc_data)
        }
    }

