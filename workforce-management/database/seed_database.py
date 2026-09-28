"""
AI-Powered Workforce Management Automation System
MongoDB High-Performance Seeding & Data Import Pipeline
--------------------------------------------------
Reads the validated Phase 1 synthetic datasets and imports them into MongoDB.
Establishes all collections, sets up proper unique & compound indexes,
and guarantees exactly 200 employees.

Features:
- High performance bulk insertion (`insert_many` with batching)
- Safe & idempotent: clean replacement per collection ensures no duplicates on re-run
- Full index coverage across all 10 modules
- Exact 200-employee guarantee (EMP001 - EMP200)
"""

import os
import sys
import json
import argparse
from pymongo import ASCENDING, DESCENDING, IndexModel

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from database.mongodb import get_db, check_connection

FIXTURES_DIR = os.path.join(ROOT_DIR, "data", "fixtures")

def load_fixture(filename: str) -> list:
    """Loads a JSON fixture file from data/fixtures/."""
    file_path = os.path.join(FIXTURES_DIR, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fixture file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_and_insert(db, collection_name: str, documents: list, batch_size: int = 5000):
    """Deletes existing documents in collection and inserts fresh documents in batches."""
    col = db[collection_name]
    col.delete_many({})
    if not documents:
        return
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        col.insert_many(batch, ordered=False)

def setup_indexes(db):
    """Creates required indexes on MongoDB collections."""
    print("Setting up MongoDB indexes...")

    # 1. Employees
    db.employees.create_indexes([
        IndexModel([("employee_id", ASCENDING)], unique=True, name="idx_employee_id_unique"),
        IndexModel([("email", ASCENDING)], unique=True, name="idx_employee_email_unique"),
        IndexModel([("department_id", ASCENDING)], name="idx_employee_department"),
        IndexModel([("manager_id", ASCENDING)], name="idx_employee_manager"),
        IndexModel([("location_id", ASCENDING)], name="idx_employee_location"),
        IndexModel([("role", ASCENDING)], name="idx_employee_role"),
        IndexModel([("employment_status", ASCENDING)], name="idx_employee_status")
    ])

    # 2. Departments
    db.departments.create_indexes([
        IndexModel([("department_id", ASCENDING)], unique=True, name="idx_department_id_unique"),
        IndexModel([("code", ASCENDING)], unique=True, name="idx_department_code_unique"),
        IndexModel([("name", ASCENDING)], unique=True, name="idx_department_name_unique")
    ])

    # 3. Locations
    db.locations.create_indexes([
        IndexModel([("location_id", ASCENDING)], unique=True, name="idx_location_id_unique"),
        IndexModel([("city", ASCENDING)], name="idx_location_city")
    ])

    # 4. Roles & Permissions
    db.roles.create_indexes([
        IndexModel([("role_name", ASCENDING)], unique=True, name="idx_role_name_unique")
    ])
    db.permissions.create_indexes([
        IndexModel([("permission_code", ASCENDING)], unique=True, name="idx_permission_code_unique")
    ])

    # 5. Attendance & Anomalies
    db.attendance.create_indexes([
        IndexModel([("attendance_id", ASCENDING)], unique=True, name="idx_attendance_id_unique"),
        IndexModel([("employee_id", ASCENDING), ("date", ASCENDING)], unique=True, name="idx_attendance_emp_date_unique"),
        IndexModel([("date", ASCENDING)], name="idx_attendance_date"),
        IndexModel([("attendance_status", ASCENDING)], name="idx_attendance_status"),
        IndexModel([("anomaly_flag", ASCENDING)], name="idx_attendance_anomaly")
    ])
    db.attendance_anomalies.create_indexes([
        IndexModel([("anomaly_id", ASCENDING)], unique=True, name="idx_anomaly_id_unique"),
        IndexModel([("attendance_id", ASCENDING)], unique=True, name="idx_anomaly_attendance_id"),
        IndexModel([("employee_id", ASCENDING)], name="idx_anomaly_emp"),
        IndexModel([("date", ASCENDING)], name="idx_anomaly_date")
    ])

    # 6. Shifts & Schedules
    db.shifts.create_indexes([
        IndexModel([("shift_id", ASCENDING)], unique=True, name="idx_shift_id_unique"),
        IndexModel([("shift_name", ASCENDING)], unique=True, name="idx_shift_name_unique")
    ])
    db.employee_shifts.create_indexes([
        IndexModel([("schedule_id", ASCENDING)], unique=True, name="idx_schedule_id_unique"),
        IndexModel([("employee_id", ASCENDING)], name="idx_emp_shifts_emp")
    ])
    db.shift_swap_requests.create_indexes([
        IndexModel([("swap_id", ASCENDING)], unique=True, name="idx_swap_id_unique"),
        IndexModel([("requester_id", ASCENDING)], name="idx_swap_requester")
    ])
    db.overtime_records.create_indexes([
        IndexModel([("overtime_id", ASCENDING)], unique=True, name="idx_overtime_id_unique"),
        IndexModel([("employee_id", ASCENDING), ("date", ASCENDING)], name="idx_overtime_emp_date")
    ])

    # 7. Leave Management
    db.leave_types.create_indexes([
        IndexModel([("leave_type_code", ASCENDING)], unique=True, name="idx_leave_type_code_unique")
    ])
    db.leave_balances.create_indexes([
        IndexModel([("balance_id", ASCENDING)], unique=True, name="idx_balance_id_unique"),
        IndexModel([("employee_id", ASCENDING), ("leave_type", ASCENDING), ("year", ASCENDING)], unique=True, name="idx_balance_emp_type_year")
    ])
    db.leave_requests.create_indexes([
        IndexModel([("leave_id", ASCENDING)], unique=True, name="idx_leave_id_unique"),
        IndexModel([("employee_id", ASCENDING)], name="idx_leave_emp"),
        IndexModel([("status", ASCENDING)], name="idx_leave_status")
    ])
    db.holidays.create_indexes([
        IndexModel([("holiday_id", ASCENDING)], unique=True, name="idx_holiday_id_unique"),
        IndexModel([("date", ASCENDING)], name="idx_holiday_date")
    ])

    # 8. Timesheets & Projects
    db.projects.create_indexes([
        IndexModel([("project_id", ASCENDING)], unique=True, name="idx_project_id_unique")
    ])
    db.timesheets.create_indexes([
        IndexModel([("timesheet_id", ASCENDING)], unique=True, name="idx_timesheet_id_unique"),
        IndexModel([("employee_id", ASCENDING), ("date", ASCENDING), ("project_id", ASCENDING)], name="idx_ts_emp_date_proj")
    ])
    db.timesheet_approvals.create_indexes([
        IndexModel([("approval_id", ASCENDING)], unique=True, name="idx_ts_approval_id")
    ])

    # 9. Payroll
    db.payroll_records.create_indexes([
        IndexModel([("payroll_id", ASCENDING)], unique=True, name="idx_payroll_id_unique"),
        IndexModel([("employee_id", ASCENDING), ("month", ASCENDING)], unique=True, name="idx_payroll_emp_month_unique"),
        IndexModel([("month", ASCENDING)], name="idx_payroll_month")
    ])
    db.payroll_components.create_indexes([
        IndexModel([("component_code", ASCENDING)], unique=True, name="idx_comp_code_unique")
    ])
    db.bonuses_incentives.create_indexes([
        IndexModel([("bonus_id", ASCENDING)], unique=True, name="idx_bonus_id_unique"),
        IndexModel([("employee_id", ASCENDING), ("month", ASCENDING)], name="idx_bonus_emp_month")
    ])
    db.payroll_exports.create_indexes([
        IndexModel([("export_id", ASCENDING)], unique=True, name="idx_export_id_unique")
    ])

    # 10. Performance
    db.performance_reviews.create_indexes([
        IndexModel([("review_id", ASCENDING)], unique=True, name="idx_review_id_unique"),
        IndexModel([("employee_id", ASCENDING)], name="idx_review_emp")
    ])
    db.performance_kpis.create_indexes([
        IndexModel([("kpi_id", ASCENDING)], unique=True, name="idx_kpi_id_unique")
    ])
    db.employee_goals.create_indexes([
        IndexModel([("goal_id", ASCENDING)], unique=True, name="idx_goal_id_unique"),
        IndexModel([("employee_id", ASCENDING)], name="idx_goal_emp")
    ])
    db.productivity_records.create_indexes([
        IndexModel([("record_id", ASCENDING)], unique=True, name="idx_prod_record_id"),
        IndexModel([("employee_id", ASCENDING), ("date", ASCENDING)], name="idx_prod_emp_date")
    ])
    db.performance_scorecards.create_indexes([
        IndexModel([("scorecard_id", ASCENDING)], unique=True, name="idx_scorecard_id_unique"),
        IndexModel([("employee_id", ASCENDING)], name="idx_scorecard_emp")
    ])

    # 11. Skills & Training
    db.skills.create_indexes([
        IndexModel([("skill_id", ASCENDING)], unique=True, name="idx_skill_id_unique"),
        IndexModel([("skill_name", ASCENDING)], unique=True, name="idx_skill_name_unique")
    ])
    db.employee_skills.create_indexes([
        IndexModel([("employee_id", ASCENDING), ("skill_id", ASCENDING)], unique=True, name="idx_emp_skills_unique")
    ])
    db.training_programs.create_indexes([
        IndexModel([("program_id", ASCENDING)], unique=True, name="idx_prog_id_unique")
    ])
    db.employee_training.create_indexes([
        IndexModel([("training_id", ASCENDING)], unique=True, name="idx_emp_tr_id_unique"),
        IndexModel([("employee_id", ASCENDING)], name="idx_emp_tr_emp")
    ])

    # 12. Workforce Planning
    db.workforce_forecasts.create_indexes([
        IndexModel([("forecast_id", ASCENDING)], unique=True, name="idx_forecast_id_unique"),
        IndexModel([("department_id", ASCENDING), ("forecast_period", ASCENDING)], name="idx_forecast_dept_period")
    ])
    db.staffing_recommendations.create_indexes([
        IndexModel([("recommendation_id", ASCENDING)], unique=True, name="idx_staff_rec_id")
    ])
    db.attrition_predictions.create_indexes([
        IndexModel([("prediction_id", ASCENDING)], unique=True, name="idx_attrition_pred_id"),
        IndexModel([("employee_id", ASCENDING)], unique=True, name="idx_attrition_emp")
    ])
    db.resource_allocations.create_indexes([
        IndexModel([("allocation_id", ASCENDING)], unique=True, name="idx_alloc_id")
    ])

    # 13. Users & Security
    db.users.create_indexes([
        IndexModel([("user_id", ASCENDING)], unique=True, name="idx_user_id_unique"),
        IndexModel([("email", ASCENDING)], unique=True, name="idx_user_email_unique"),
        IndexModel([("employee_id", ASCENDING)], name="idx_user_emp"),
        IndexModel([("role", ASCENDING)], name="idx_user_role")
    ])
    db.audit_logs.create_indexes([
        IndexModel([("log_id", ASCENDING)], unique=True, name="idx_audit_log_id"),
        IndexModel([("timestamp", DESCENDING)], name="idx_audit_timestamp"),
        IndexModel([("user_id", ASCENDING)], name="idx_audit_user"),
        IndexModel([("action", ASCENDING)], name="idx_audit_action")
    ])

    # 14. Notifications & Workflows
    db.notifications.create_indexes([
        IndexModel([("notification_id", ASCENDING)], unique=True, name="idx_notif_id_unique"),
        IndexModel([("employee_id", ASCENDING), ("is_read", ASCENDING)], name="idx_notif_emp_read"),
        IndexModel([("recipient_employee_id", ASCENDING), ("is_read", ASCENDING)], name="idx_notif_recip_read"),
        IndexModel([("dedup_key", ASCENDING)], unique=False, sparse=True, name="idx_notif_dedup"),
        IndexModel([("created_at", DESCENDING)], name="idx_notif_created_at")
    ])
    db.notification_preferences.create_indexes([
        IndexModel([("employee_id", ASCENDING)], unique=True, name="idx_notif_pref_emp_unique")
    ])
    db.workflow_events.create_indexes([
        IndexModel([("event_id", ASCENDING)], unique=True, name="idx_wf_event_id_unique"),
        IndexModel([("event_type", ASCENDING)], name="idx_wf_event_type"),
        IndexModel([("created_at", DESCENDING)], name="idx_wf_event_created_at")
    ])
    db.workflow_executions.create_indexes([
        IndexModel([("execution_id", ASCENDING)], unique=True, name="idx_wf_exec_id_unique"),
        IndexModel([("event_id", ASCENDING)], name="idx_wf_exec_event_id"),
        IndexModel([("status", ASCENDING)], name="idx_wf_exec_status")
    ])

    print("All MongoDB indexes established successfully.")

# ---------------------------------------------------------
# Seed Pipeline Execution
# ---------------------------------------------------------

def seed_database():
    conn_info = check_connection()
    if not conn_info["ok"]:
        print(f"[FATAL] Cannot connect to MongoDB: {conn_info.get('error')}", file=sys.stderr)
        sys.exit(1)

    db = get_db()
    print("=" * 60)
    print("AI WORKFORCE MANAGEMENT SYSTEM - MONGODB SEED PIPELINE")
    print(f"Target Database: {db.name}")
    print(f"MongoDB URI:     {conn_info['uri']}")
    print("=" * 60)

    # 1. Locations
    print("Importing locations...")
    clean_and_insert(db, "locations", load_fixture("locations.json"))

    # 2. Departments
    print("Importing departments...")
    clean_and_insert(db, "departments", load_fixture("departments.json"))

    # 3. Roles & Permissions Master Data
    print("Importing roles and permissions...")
    roles_data = [
        {"role_name": "ADMIN", "description": "Full system administrator with unrestricted privileges", "permissions": ["*"]},
        {"role_name": "HR", "description": "Human Resources personnel managing employee onboarding, leave, and payroll", "permissions": ["employee:*", "leave:*", "payroll:*", "attendance:read", "reports:*"]},
        {"role_name": "MANAGER", "description": "Team lead or department head managing reporting direct reports", "permissions": ["employee:read", "attendance:team", "leave:approve", "timesheet:approve", "performance:review"]},
        {"role_name": "EMPLOYEE", "description": "Standard workforce member with self-service portal access", "permissions": ["profile:read", "attendance:self", "leave:apply", "timesheet:self", "payroll:self"]}
    ]
    clean_and_insert(db, "roles", roles_data)

    permissions_catalog = [
        {"permission_code": "employee:read", "category": "Employee", "description": "View employee profile details"},
        {"permission_code": "employee:write", "category": "Employee", "description": "Create and edit employee profiles"},
        {"permission_code": "attendance:clock", "category": "Attendance", "description": "Perform clock-in and clock-out"},
        {"permission_code": "attendance:team", "category": "Attendance", "description": "View direct reports attendance"},
        {"permission_code": "leave:apply", "category": "Leave", "description": "Submit leave applications"},
        {"permission_code": "leave:approve", "category": "Leave", "description": "Approve or reject team leave requests"},
        {"permission_code": "timesheet:submit", "category": "Timesheet", "description": "Log and submit project timesheets"},
        {"permission_code": "timesheet:approve", "category": "Timesheet", "description": "Approve project timesheets"},
        {"permission_code": "payroll:view", "category": "Payroll", "description": "View own salary slips"},
        {"permission_code": "payroll:process", "category": "Payroll", "description": "Calculate and process corporate payroll"},
        {"permission_code": "performance:review", "category": "Performance", "description": "Conduct performance appraisals"},
        {"permission_code": "reports:view", "category": "Reports", "description": "Access enterprise workforce analytics"}
    ]
    clean_and_insert(db, "permissions", permissions_catalog)

    # 4. Employees (Strictly 200 records EMP001 to EMP200)
    print("Importing exactly 200 employees...")
    employees_data = load_fixture("employees.json")
    if len(employees_data) != 200:
        raise ValueError(f"CRITICAL ERROR: Expected exactly 200 employees, found {len(employees_data)}!")
    clean_and_insert(db, "employees", employees_data)

    # 5. Shifts & Employee Shifts
    print("Importing shifts and shift schedules...")
    clean_and_insert(db, "shifts", load_fixture("shifts.json"))
    clean_and_insert(db, "employee_shifts", load_fixture("employee_shifts.json"))

    # Shift Swap Requests
    shift_swaps = [
        {"swap_id": "SWP0001", "requester_id": "EMP036", "target_employee_id": "EMP037", "shift_id": "SH02", "target_shift_id": "SH03", "requested_date": "2026-03-25", "status": "Pending", "reason": "Family engagement", "approved_by": None},
        {"swap_id": "SWP0002", "requester_id": "EMP120", "target_employee_id": "EMP121", "shift_id": "SH03", "target_shift_id": "SH01", "requested_date": "2026-03-26", "status": "Approved", "reason": "Doctor appointment", "approved_by": "EMP024"}
    ]
    clean_and_insert(db, "shift_swap_requests", shift_swaps)

    # 6. Attendance, Anomalies, and Overtime
    print("Importing attendance records (~24,600 logs)...")
    attendance_data = load_fixture("attendance.json")
    clean_and_insert(db, "attendance", attendance_data, batch_size=5000)

    # Extract anomalies and overtime
    print("Extracting attendance anomalies and overtime records...")
    anomalies = [d for d in attendance_data if d.get("anomaly_flag") == 1]
    anomaly_docs = []
    for a in anomalies:
        anomaly_docs.append({
            "anomaly_id": f"ANO_{a['attendance_id']}",
            "attendance_id": a["attendance_id"],
            "employee_id": a["employee_id"],
            "date": a["date"],
            "anomaly_type": "OVERTIME" if "overtime" in str(a.get("anomaly_reason", "")).lower() else ("CHECKOUT" if "check-out" in str(a.get("anomaly_reason", "")).lower() else "TIMING"),
            "reason": a.get("anomaly_reason"),
            "severity": "HIGH" if "exceeding" in str(a.get("anomaly_reason", "")).lower() else "MEDIUM",
            "status": "Investigating"
        })
    clean_and_insert(db, "attendance_anomalies", anomaly_docs)

    ot_records = []
    ot_counter = 1
    for a in attendance_data:
        if a.get("overtime_hours", 0.0) > 0.0:
            ot_records.append({
                "overtime_id": f"OT{ot_counter:06d}",
                "employee_id": a["employee_id"],
                "date": a["date"],
                "overtime_hours": a["overtime_hours"],
                "shift_id": a["shift_id"],
                "status": "Approved" if a["date"] < "2026-03-15" else "Pending",
                "approved_by": "EMP002"
            })
            ot_counter += 1
    clean_and_insert(db, "overtime_records", ot_records, batch_size=5000)

    # 7. Leave Management
    print("Importing leave types, balances, requests, and holidays...")
    leave_types_data = [
        {"leave_type_code": "AL", "name": "Annual Leave", "max_days_per_year": 18, "is_carry_forward": True, "requires_approval": True},
        {"leave_type_code": "SL", "name": "Sick Leave", "max_days_per_year": 12, "is_carry_forward": False, "requires_approval": True},
        {"leave_type_code": "CL", "name": "Casual Leave", "max_days_per_year": 10, "is_carry_forward": False, "requires_approval": True},
        {"leave_type_code": "EL", "name": "Emergency Leave", "max_days_per_year": 5, "is_carry_forward": False, "requires_approval": True},
        {"leave_type_code": "ML", "name": "Maternity/Paternity Leave", "max_days_per_year": 90, "is_carry_forward": False, "requires_approval": True}
    ]
    clean_and_insert(db, "leave_types", leave_types_data)
    clean_and_insert(db, "leave_balances", load_fixture("leave_balances.json"))
    clean_and_insert(db, "leave_requests", load_fixture("leave_requests.json"))
    clean_and_insert(db, "holidays", load_fixture("company_holidays.json"))

    # 8. Projects & Timesheets
    print("Importing projects, timesheets, and approvals...")
    clean_and_insert(db, "projects", load_fixture("projects.json"))
    timesheets_data = load_fixture("timesheets.json")
    clean_and_insert(db, "timesheets", timesheets_data, batch_size=5000)

    ts_approvals = []
    for ts in timesheets_data[:200]:
        ts_approvals.append({
            "approval_id": f"TSA_{ts['timesheet_id']}",
            "timesheet_id": ts["timesheet_id"],
            "approver_id": "EMP011",
            "approval_date": ts["date"],
            "status": ts["status"],
            "comments": "Approved as per sprint deliverables."
        })
    clean_and_insert(db, "timesheet_approvals", ts_approvals)

    # 9. Payroll Management
    print("Importing payroll records, components, and bonuses...")
    payroll_data = load_fixture("payroll.json")
    clean_and_insert(db, "payroll_records", payroll_data)

    payroll_components_data = [
        {"component_code": "BASE", "name": "Basic Salary", "type": "EARNING", "taxable": True},
        {"component_code": "OT", "name": "Overtime Compensation", "type": "EARNING", "taxable": True},
        {"component_code": "BONUS", "name": "Festival & Performance Bonus", "type": "EARNING", "taxable": True},
        {"component_code": "INCENTIVE", "name": "Quarterly Incentive", "type": "EARNING", "taxable": True},
        {"component_code": "PF", "name": "Provident Fund", "type": "DEDUCTION", "taxable": False},
        {"component_code": "TDS", "name": "Income Tax Deducted at Source", "type": "DEDUCTION", "taxable": False},
        {"component_code": "LEAVE_DED", "name": "Unpaid Leave Deduction", "type": "DEDUCTION", "taxable": False}
    ]
    clean_and_insert(db, "payroll_components", payroll_components_data)

    bonuses_data = []
    b_count = 1
    for p in payroll_data:
        if p.get("bonuses", 0.0) > 0.0 or p.get("incentives", 0.0) > 0.0:
            bonuses_data.append({
                "bonus_id": f"BON{b_count:05d}",
                "employee_id": p["employee_id"],
                "month": p["month"],
                "bonus_amount": p.get("bonuses", 0.0),
                "incentive_amount": p.get("incentives", 0.0),
                "reason": "Diwali Festival Bonus" if p["month"] == "2025-10" else "Performance Incentive",
                "approved_by": "EMP001"
            })
            b_count += 1
    clean_and_insert(db, "bonuses_incentives", bonuses_data)

    payroll_exports = [
        {"export_id": "EXP001", "month": "2025-10", "format": "CSV", "exported_by": "EMP003", "exported_at": "2025-11-01 10:00:00", "records_count": 200, "status": "COMPLETED"},
        {"export_id": "EXP002", "month": "2025-11", "format": "EXCEL", "exported_by": "EMP003", "exported_at": "2025-12-01 10:00:00", "records_count": 200, "status": "COMPLETED"},
        {"export_id": "EXP003", "month": "2025-12", "format": "CSV", "exported_by": "EMP003", "exported_at": "2026-01-02 10:00:00", "records_count": 200, "status": "COMPLETED"},
        {"export_id": "EXP004", "month": "2026-01", "format": "EXCEL", "exported_by": "EMP003", "exported_at": "2026-02-01 10:00:00", "records_count": 200, "status": "COMPLETED"},
        {"export_id": "EXP005", "month": "2026-02", "format": "CSV", "exported_by": "EMP003", "exported_at": "2026-03-01 10:00:00", "records_count": 200, "status": "COMPLETED"}
    ]
    clean_and_insert(db, "payroll_exports", payroll_exports)

    # 10. Performance Management
    print("Importing performance reviews, KPIs, and scorecards...")
    reviews_data = load_fixture("performance_reviews.json")
    clean_and_insert(db, "performance_reviews", reviews_data)

    kpis = [
        {"kpi_id": "KPI01", "department_id": "DEP01", "kpi_name": "Sprint Velocity & Delivery", "target": 90.0, "unit": "Percentage"},
        {"kpi_id": "KPI02", "department_id": "DEP02", "kpi_name": "Model Accuracy & Production Pipeline", "target": 88.0, "unit": "Percentage"},
        {"kpi_id": "KPI03", "department_id": "DEP06", "kpi_name": "Quarterly Sales Target Realization", "target": 100.0, "unit": "Percentage"},
        {"kpi_id": "KPI04", "department_id": "DEP09", "kpi_name": "First Contact Resolution Rate", "target": 92.0, "unit": "Percentage"}
    ]
    clean_and_insert(db, "performance_kpis", kpis)

    goals = []
    prod_records = []
    scorecards = []
    for r in reviews_data:
        eid = r["employee_id"]
        goals.append({
            "goal_id": f"GL_{eid}",
            "employee_id": eid,
            "title": "Quarterly Strategic Milestone Completion",
            "completion_percentage": r["goal_completion"],
            "due_date": "2026-03-31",
            "status": "Achieved" if r["goal_completion"] >= 75.0 else "In Progress"
        })
        prod_records.append({
            "record_id": f"PRD_{eid}",
            "employee_id": eid,
            "date": "2026-03-20",
            "productivity_score": r["productivity_score"],
            "tasks_completed": int(r["productivity_score"] / 10),
            "status": "Recorded"
        })
        scorecards.append({
            "scorecard_id": f"SC_{r['review_id']}",
            "employee_id": eid,
            "period": "FY 2025-26 Annual",
            "overall_score": r["productivity_score"],
            "rating": r["performance_rating"],
            "kpi_attainment": r["kpi_score"],
            "goal_attainment": r["goal_completion"],
            "status": "Finalized"
        })
    clean_and_insert(db, "employee_goals", goals)
    clean_and_insert(db, "productivity_records", prod_records)
    clean_and_insert(db, "performance_scorecards", scorecards)

    # 11. Skills & Training
    print("Importing skills taxonomy and employee skill proficiencies...")
    clean_and_insert(db, "skills", load_fixture("skills.json"))
    clean_and_insert(db, "employee_skills", load_fixture("employee_skills.json"))

    training_programs = [
        {"program_id": "TRP01", "name": "Advanced Python & Microservices", "skill": "Python", "duration_hours": 40},
        {"program_id": "TRP02", "name": "Applied Machine Learning at Scale", "skill": "Machine Learning", "duration_hours": 50},
        {"program_id": "TRP03", "name": "Modern Cloud Architecture with AWS", "skill": "AWS", "duration_hours": 45},
        {"program_id": "TRP04", "name": "Data Analytics with Power BI & SQL", "skill": "Power BI", "duration_hours": 35},
        {"program_id": "TRP05", "name": "Full Stack React & Modern UI", "skill": "React", "duration_hours": 40},
        {"program_id": "TRP06", "name": "Kubernetes & DevOps Pipelines", "skill": "DevOps", "duration_hours": 40},
        {"program_id": "TRP07", "name": "Strategic Leadership & Communication", "skill": "Communication", "duration_hours": 25},
        {"program_id": "TRP08", "name": "Enterprise Cybersecurity Fundamentals", "skill": "Cybersecurity", "duration_hours": 30}
    ]
    clean_and_insert(db, "training_programs", training_programs)

    training_records_data = load_fixture("training_records.json")
    recommendations_data = load_fixture("training_recommendations.json")
    training_docs = []
    for tr in training_records_data:
        d = dict(tr)
        d["type"] = "COMPLETED"
        training_docs.append(d)
    for rec in recommendations_data:
        training_docs.append({
            "training_id": rec["recommendation_id"],
            "employee_id": rec["employee_id"],
            "training_name": rec["recommended_course"],
            "skill": rec["target_skill"],
            "completion_status": "Recommended",
            "type": "AI_RECOMMENDATION",
            "reason": rec.get("reason"),
            "start_date": None,
            "completion_date": None,
            "score": None
        })
    clean_and_insert(db, "employee_training", training_docs)

    # 12. Workforce Planning
    print("Importing workforce planning demo entities...")
    forecasts = [
        {"forecast_id": "FC001", "department_id": "DEP01", "forecast_period": "Q3-2026", "projected_headcount_need": 62, "current_headcount": 55, "recommended_hires": 7, "budget_impact": 8400000.0, "status": "Draft"},
        {"forecast_id": "FC002", "department_id": "DEP02", "forecast_period": "Q3-2026", "projected_headcount_need": 29, "current_headcount": 25, "recommended_hires": 4, "budget_impact": 5600000.0, "status": "Draft"},
        {"forecast_id": "FC003", "department_id": "DEP06", "forecast_period": "Q3-2026", "projected_headcount_need": 26, "current_headcount": 22, "recommended_hires": 4, "budget_impact": 4200000.0, "status": "Draft"}
    ]
    clean_and_insert(db, "workforce_forecasts", forecasts)

    staffing_recs = [
        {"recommendation_id": "SR001", "department_id": "DEP01", "target_role": "Cloud DevOps Engineer", "priority": "HIGH", "recommended_count": 3, "rationale": "High workload spikes and cloud migration projects in Q2/Q3."},
        {"recommendation_id": "SR002", "department_id": "DEP02", "target_role": "MLOps Research Associate", "priority": "MEDIUM", "recommended_count": 2, "rationale": "Expanded AI pilot deployments require automated model serving pipelines."}
    ]
    clean_and_insert(db, "staffing_recommendations", staffing_recs)

    attrition_docs = []
    for emp in employees_data:
        eid = emp["employee_id"]
        is_notice = emp.get("employment_status") == "On Notice"
        risk_score = 0.88 if is_notice else round(0.10 + (int(eid[3:]) % 40) * 0.015, 2)
        attrition_docs.append({
            "prediction_id": f"ATT_PRED_{eid}",
            "employee_id": eid,
            "department_id": emp["department_id"],
            "risk_score": risk_score,
            "risk_category": "HIGH" if risk_score > 0.65 else ("MEDIUM" if risk_score > 0.35 else "LOW"),
            "contributing_factors": ["Notice Period Active"] if is_notice else ["Compensation Benchmark", "Project Duration"],
            "last_evaluated": "2026-03-20"
        })
    clean_and_insert(db, "attrition_predictions", attrition_docs)

    allocations = [
        {"allocation_id": "ALC001", "project_id": "PRJ01", "employee_id": "EMP011", "hours_per_week": 40.0, "status": "Active"},
        {"allocation_id": "ALC002", "project_id": "PRJ02", "employee_id": "EMP017", "hours_per_week": 40.0, "status": "Active"},
        {"allocation_id": "ALC003", "project_id": "PRJ03", "employee_id": "EMP012", "hours_per_week": 40.0, "status": "Active"}
    ]
    clean_and_insert(db, "resource_allocations", allocations)

    # 13. Users & Security Accounts
    print("Importing user authentication credentials & audit logs...")
    clean_and_insert(db, "users", load_fixture("user_accounts.json"))

    audit_logs = [
        {"log_id": "LOG00001", "timestamp": "2026-03-23 10:00:00", "user_id": "USR0001", "action": "DATABASE_INITIALIZATION", "details": "Imported Phase 1 synthetic datasets into MongoDB collections.", "ip_address": "127.0.0.1"},
        {"log_id": "LOG00002", "timestamp": "2026-03-23 10:05:00", "user_id": "USR0001", "action": "INDEX_CREATION", "details": "Established unique and compound indexes on all collections.", "ip_address": "127.0.0.1"}
    ]
    clean_and_insert(db, "audit_logs", audit_logs)

    # 14. Notifications & Preferences
    print("Importing notifications & preferences...")
    clean_and_insert(db, "notifications", load_fixture("notifications.json"))
    pref_docs = []
    for emp in employees_data:
        pref_docs.append({
            "employee_id": emp["employee_id"],
            "email_notifications": True,
            "shift_reminders": True,
            "leave_status_alerts": True,
            "payroll_alerts": True,
            "anniversary_alerts": True
        })
    clean_and_insert(db, "notification_preferences", pref_docs)

    # Setup indexes after insertion
    setup_indexes(db)

    print("=" * 60)
    print("MONGODB SEEDING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print_summary(db)

def print_summary(db):
    """Prints a clean tabular summary of document counts across all collections."""
    collections = sorted(db.list_collection_names())
    print("\nDATABASE COLLECTION INVENTORY:")
    print("-" * 50)
    print(f"{'Collection Name':<30} {'Document Count':>15}")
    print("-" * 50)

    total_docs = 0
    for name in collections:
        if name.startswith("system."):
            continue
        count = db[name].count_documents({})
        total_docs += count
        print(f"{name:<30} {count:>15,}")

    print("-" * 50)
    print(f"{'TOTAL DOCUMENTS':<30} {total_docs:>15,}")
    print("-" * 50)

    emp_count = db.employees.count_documents({})
    print(f"\nCRITICAL VERIFICATION: Employees Count = {emp_count} (Required: EXACTLY 200)")
    if emp_count != 200:
        print(f"[FATAL] Employee count mismatch! Expected 200, got {emp_count}", file=sys.stderr)
        sys.exit(1)
    else:
        print("[SUCCESS] Exactly 200 employees verified in MongoDB (EMP001 - EMP200).")

if __name__ == "__main__":
    seed_database()
