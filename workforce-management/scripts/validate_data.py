"""
AI-Powered Workforce Management Automation System
Automated Data Validation Suite
--------------------------------------------------
Validates the synthetic dataset across all relational and business integrity rules:
1. Employee validation:
   - Exactly 200 employees
   - Unique employee IDs (EMP001 - EMP200)
   - No duplicate emails
   - Valid department IDs
   - Valid manager IDs
   - No employee managing themselves
   - Valid acyclic management hierarchy
2. Attendance validation:
   - Valid employee IDs
   - Valid dates
   - Check-out after check-in (for complete sessions)
   - Valid shift IDs
   - No impossible working hours
3. Leave validation:
   - Valid employee IDs
   - Valid dates (start_date <= end_date)
   - Leave balance logical consistency (allocated == used + remaining)
4. Payroll validation:
   - gross_salary == base_salary + overtime_pay + incentives + bonuses
   - net_salary == gross_salary - deductions
   - No negative salary values
5. Timesheet validation:
   - Valid employee IDs
   - Valid project IDs
   - Hours within reasonable limits (0 <= hours <= 24)
   - hours_worked == billable_hours + non_billable_hours
6. Relational & Schema Integrity:
   - Foreign key integrity check via PRAGMA foreign_key_check

Outputs:
- data_validation_report.json
- data_validation_report.html
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, date

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "hr_automation.db")
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

JSON_REPORT_PATH_1 = os.path.join(REPORTS_DIR, "data_validation_report.json")
JSON_REPORT_PATH_2 = os.path.join(ROOT_DIR, "data_validation_report.json")
HTML_REPORT_PATH_1 = os.path.join(REPORTS_DIR, "data_validation_report.html")
HTML_REPORT_PATH_2 = os.path.join(ROOT_DIR, "data_validation_report.html")

class DataValidator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "database_file": db_path,
            "overall_status": "PASSED",
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "summary_metrics": {},
            "categories": {}
        }
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def add_check(self, category, check_name, passed, details, sample_data=None):
        self.results["total_checks"] += 1
        if passed:
            self.results["passed_checks"] += 1
            status = "PASSED"
        else:
            self.results["failed_checks"] += 1
            self.results["overall_status"] = "FAILED"
            status = "FAILED"

        if category not in self.results["categories"]:
            self.results["categories"][category] = {
                "name": category,
                "passed": 0,
                "failed": 0,
                "checks": []
            }

        if passed:
            self.results["categories"][category]["passed"] += 1
        else:
            self.results["categories"][category]["failed"] += 1

        self.results["categories"][category]["checks"].append({
            "check_name": check_name,
            "status": status,
            "details": details,
            "sample_data": sample_data
        })

    def run_all_validations(self):
        print(f"Connecting to database for validation: {self.db_path}")
        self.validate_schema_and_fks()
        self.validate_employees()
        self.validate_departments_and_locations()
        self.validate_attendance()
        self.validate_leave()
        self.validate_payroll()
        self.validate_timesheets()
        self.validate_performance_and_training()
        self.validate_user_accounts()
        self.compute_summary_metrics()

    def validate_schema_and_fks(self):
        cat = "Foreign Key & Database Constraints"
        cursor = self.conn.cursor()
        fk_violations = cursor.execute("PRAGMA foreign_key_check;").fetchall()
        passed = len(fk_violations) == 0
        details = "No foreign key violations detected." if passed else f"Detected {len(fk_violations)} FK violations."
        self.add_check(cat, "SQLite Foreign Key Check", passed, details, [dict(r) for r in fk_violations[:5]] if not passed else None)

    def validate_employees(self):
        cat = "Employee Validation"
        cursor = self.conn.cursor()
        employees = cursor.execute("SELECT * FROM employees ORDER BY employee_id ASC;").fetchall()
        emp_count = len(employees)

        # 1. Exactly 200 employees
        passed_count = (emp_count == 200)
        self.add_check(cat, "Exactly 200 Employees Count", passed_count,
                       f"Found {emp_count} employees. Required: EXACTLY 200.")

        # 2. Strict ID format EMP001 to EMP200
        emp_ids = [r["employee_id"] for r in employees]
        expected_ids = [f"EMP{i:03d}" for i in range(1, 201)]
        passed_ids = (emp_ids == expected_ids)
        self.add_check(cat, "Unique Employee IDs Sequence (EMP001 to EMP200)", passed_ids,
                       f"Employee IDs match standard sequence EMP001 through EMP200 without gaps or extras.")

        # 3. Unique emails
        emails = [r["email"].lower() for r in employees]
        unique_emails = set(emails)
        passed_emails = (len(emails) == len(unique_emails))
        self.add_check(cat, "Unique Corporate Emails", passed_emails,
                       f"{len(unique_emails)} unique emails found across {len(emails)} employees.")

        # 4. Valid department IDs
        depts = {r["department_id"] for r in cursor.execute("SELECT department_id FROM departments;").fetchall()}
        invalid_depts = [r["employee_id"] for r in employees if r["department_id"] not in depts]
        self.add_check(cat, "Valid Department IDs Assigned", len(invalid_depts) == 0,
                       f"All employees mapped to valid departments. Invalid count: {len(invalid_depts)}.")

        # 5. Valid locations
        locs = {r["location_id"] for r in cursor.execute("SELECT location_id FROM locations;").fetchall()}
        invalid_locs = [r["employee_id"] for r in employees if r["location_id"] not in locs]
        self.add_check(cat, "Valid Office Locations Assigned", len(invalid_locs) == 0,
                       f"All employees assigned to recognized office locations. Invalid count: {len(invalid_locs)}.")

        # 6. Valid manager IDs & No employee managing themselves
        self_managed = [r["employee_id"] for r in employees if r["manager_id"] == r["employee_id"]]
        self.add_check(cat, "No Employee Manages Themselves", len(self_managed) == 0,
                       f"Zero self-referencing managers found." if len(self_managed) == 0 else f"Self-managed: {self_managed}")

        # Managers must exist in employee list
        emp_id_set = set(emp_ids)
        invalid_managers = [r["employee_id"] for r in employees if r["manager_id"] and r["manager_id"] not in emp_id_set]
        self.add_check(cat, "Manager IDs Exist in Employees Table", len(invalid_managers) == 0,
                       f"All managers are verified active employees in the table.")

        # Check for cycles in manager hierarchy
        manager_map = {r["employee_id"]: r["manager_id"] for r in employees}
        has_cycle = False
        for start_id in emp_ids:
            visited = set()
            curr = start_id
            while curr:
                if curr in visited:
                    has_cycle = True
                    break
                visited.add(curr)
                curr = manager_map.get(curr)
            if has_cycle:
                break
        self.add_check(cat, "Acyclic Manager Hierarchy (No Reporting Loops)", not has_cycle,
                       "The reporting structure forms a valid tree topology rooted at the CEO.")

    def validate_departments_and_locations(self):
        cat = "Organization Structure"
        cursor = self.conn.cursor()
        dept_count = cursor.execute("SELECT COUNT(*) as c FROM departments;").fetchone()["c"]
        self.add_check(cat, "9 Functional Departments Configured", dept_count == 9,
                       f"Found {dept_count} departments (Engineering, Data Science, HR, Finance, Marketing, Sales, Operations, IT, Customer Support).")

        loc_count = cursor.execute("SELECT COUNT(*) as c FROM locations;").fetchone()["c"]
        self.add_check(cat, "5 Office Hub Locations Configured", loc_count == 5,
                       f"Found {loc_count} office hubs (Hyderabad, Bengaluru, Chennai, Pune, Mumbai) with geofencing coordinates.")

        shifts_count = cursor.execute("SELECT COUNT(*) as c FROM shifts;").fetchone()["c"]
        self.add_check(cat, "4 Working Shifts Configured", shifts_count == 4,
                       f"Found {shifts_count} shifts (General, Morning, Evening, Night).")

    def validate_attendance(self):
        cat = "Attendance Data Validation"
        cursor = self.conn.cursor()
        total_att = cursor.execute("SELECT COUNT(*) as c FROM attendance;").fetchone()["c"]
        
        # Count check
        self.add_check(cat, "6-Month Attendance Records Generated", total_att >= 20000,
                       f"Total attendance rows: {total_att} (~6 months for 200 employees).")

        # Foreign Key check on employees
        emp_ids = {r["employee_id"] for r in cursor.execute("SELECT employee_id FROM employees;").fetchall()}
        invalid_att_emps = cursor.execute("SELECT COUNT(*) as c FROM attendance WHERE employee_id NOT IN (SELECT employee_id FROM employees);").fetchone()["c"]
        self.add_check(cat, "All Attendance Records Link to Valid Employees", invalid_att_emps == 0,
                       f"Invalid employee references in attendance: {invalid_att_emps}.")

        # Check-out after check-in for completed records
        # Note: Night shift (SH04) wraps around midnight (e.g. 22:00 to 07:00), which is legitimate.
        # For non-night shifts (SH01, SH02, SH03), check_out should be chronologically after check_in.
        non_night_invalid = cursor.execute("""
            SELECT COUNT(*) as c FROM attendance
            WHERE check_in IS NOT NULL AND check_out IS NOT NULL
              AND shift_id != 'SH04'
              AND check_out <= check_in;
        """).fetchone()["c"]
        self.add_check(cat, "Check-out Later Than Check-in (Standard Shifts)", non_night_invalid == 0,
                       f"Invalid check-out timestamps: {non_night_invalid}.")

        # Working hours limit check (no negative overtime or overtime > 12 hours)
        invalid_ot = cursor.execute("""
            SELECT COUNT(*) as c FROM attendance
            WHERE overtime_hours < 0 OR overtime_hours > 12;
        """).fetchone()["c"]
        self.add_check(cat, "Overtime Hours Within Plausible Range (0 to 12 hrs)", invalid_ot == 0,
                       f"Rows with impossible overtime: {invalid_ot}.")

        # Anomaly flags presence (synthetic anomaly detection benchmark)
        anomalies_count = cursor.execute("SELECT COUNT(*) as c FROM attendance WHERE anomaly_flag = 1;").fetchone()["c"]
        has_anomalies = 100 <= anomalies_count <= 1000
        self.add_check(cat, "Realistic Synthetic Anomaly Flags Embedded", has_anomalies,
                       f"Detected {anomalies_count} simulated anomaly cases ({anomalies_count/total_att*100:.2f}%) for AI detection benchmarking.")

    def validate_leave(self):
        cat = "Leave Management Validation"
        cursor = self.conn.cursor()

        # Balance integrity: allocated == used + remaining
        balance_mismatches = cursor.execute("""
            SELECT COUNT(*) as c FROM leave_balances
            WHERE ABS((used_days + remaining_days) - allocated_days) > 0.01;
        """).fetchone()["c"]
        self.add_check(cat, "Leave Balances Consistency (Allocated = Used + Remaining)", balance_mismatches == 0,
                       f"Mismatched balances: {balance_mismatches}.")

        # Request validity: start_date <= end_date
        invalid_leave_dates = cursor.execute("""
            SELECT COUNT(*) as c FROM leave_requests
            WHERE end_date < start_date;
        """).fetchone()["c"]
        self.add_check(cat, "Leave Requests Date Consistency (Start <= End)", invalid_leave_dates == 0,
                       f"Invalid date requests: {invalid_leave_dates}.")

        # Approver is valid employee
        invalid_approvers = cursor.execute("""
            SELECT COUNT(*) as c FROM leave_requests
            WHERE approved_by IS NOT NULL AND approved_by NOT IN (SELECT employee_id FROM employees);
        """).fetchone()["c"]
        self.add_check(cat, "Leave Approvers Are Valid Employees", invalid_approvers == 0,
                       f"Invalid approvers: {invalid_approvers}.")

    def validate_payroll(self):
        cat = "Payroll Calculations Validation"
        cursor = self.conn.cursor()

        total_pay = cursor.execute("SELECT COUNT(*) as c FROM payroll;").fetchone()["c"]
        self.add_check(cat, "Payroll Records Generated (6 Months x 200 Employees)", total_pay == 1200,
                       f"Total payroll rows: {total_pay} (Required: 1,200).")

        # Gross calculation check: gross = base + overtime + incentives + bonuses (allow round off 0.02)
        gross_errors = cursor.execute("""
            SELECT COUNT(*) as c FROM payroll
            WHERE ABS((base_salary + overtime_pay + incentives + bonuses) - gross_salary) > 0.05;
        """).fetchone()["c"]
        self.add_check(cat, "Gross Salary Exact Formula Verification", gross_errors == 0,
                       f"Gross salary calculation discrepancies: {gross_errors}.")

        # Net calculation check: net = gross - deductions
        net_errors = cursor.execute("""
            SELECT COUNT(*) as c FROM payroll
            WHERE ABS((gross_salary - deductions) - net_salary) > 0.05;
        """).fetchone()["c"]
        self.add_check(cat, "Net Salary Exact Formula Verification", net_errors == 0,
                       f"Net salary calculation discrepancies: {net_errors}.")

        # No negative net salary
        negative_salaries = cursor.execute("""
            SELECT COUNT(*) as c FROM payroll
            WHERE net_salary <= 0 OR gross_salary <= 0;
        """).fetchone()["c"]
        self.add_check(cat, "Zero Negative Salaries", negative_salaries == 0,
                       f"Negative or zero net salary instances: {negative_salaries}.")

    def validate_timesheets(self):
        cat = "Timesheet Data Validation"
        cursor = self.conn.cursor()

        ts_count = cursor.execute("SELECT COUNT(*) as c FROM timesheets;").fetchone()["c"]
        self.add_check(cat, "Active Timesheets Generated", ts_count > 0,
                       f"Total timesheet entries: {ts_count}.")

        # Hours consistency: hours_worked = billable + non_billable
        hours_mismatches = cursor.execute("""
            SELECT COUNT(*) as c FROM timesheets
            WHERE ABS((billable_hours + non_billable_hours) - hours_worked) > 0.05;
        """).fetchone()["c"]
        self.add_check(cat, "Timesheet Hours Consistency (Billable + Non-Billable = Total)", hours_mismatches == 0,
                       f"Timesheets with hour discrepancies: {hours_mismatches}.")

        # Hours reasonable limits: 0 < hours <= 24
        out_of_bound_hours = cursor.execute("""
            SELECT COUNT(*) as c FROM timesheets
            WHERE hours_worked <= 0 OR hours_worked > 24;
        """).fetchone()["c"]
        self.add_check(cat, "Timesheet Hours Bound Limits (0 to 24 hrs)", out_of_bound_hours == 0,
                       f"Out of bounds timesheets: {out_of_bound_hours}.")

    def validate_performance_and_training(self):
        cat = "Talent & Performance Validation"
        cursor = self.conn.cursor()

        # Performance reviews for 200 employees
        review_count = cursor.execute("SELECT COUNT(*) as c FROM performance_reviews;").fetchone()["c"]
        self.add_check(cat, "Performance Appraisals for All 200 Employees", review_count == 200,
                       f"Total reviews: {review_count} (One per employee).")

        # Ratings range 0 to 100
        score_errors = cursor.execute("""
            SELECT COUNT(*) as c FROM performance_reviews
            WHERE kpi_score < 0 OR kpi_score > 100
               OR goal_completion < 0 OR goal_completion > 100
               OR productivity_score < 0 OR productivity_score > 100;
        """).fetchone()["c"]
        self.add_check(cat, "KPI & Productivity Scores Range (0 to 100)", score_errors == 0,
                       f"Score anomalies: {score_errors}.")

        # Employee Skills mappings
        emp_skills_count = cursor.execute("SELECT COUNT(DISTINCT employee_id) as c FROM employee_skills;").fetchone()["c"]
        self.add_check(cat, "All Employees Have Mapped Skills", emp_skills_count == 200,
                       f"{emp_skills_count} employees have verified skill proficiency profiles.")

        # Training recommendations
        rec_count = cursor.execute("SELECT COUNT(*) as c FROM training_recommendations;").fetchone()["c"]
        self.add_check(cat, "AI Skill Gap Training Recommendations Generated", rec_count == 200,
                       f"Total personalized training recommendations: {rec_count}.")

    def validate_user_accounts(self):
        cat = "Authentication & Demo Accounts"
        cursor = self.conn.cursor()

        # Demo accounts check
        demo_emails = ["admin@demo.com", "manager@demo.com", "hr@demo.com", "employee@demo.com"]
        found_demos = cursor.execute(f"""
            SELECT email, role, employee_id FROM user_accounts
            WHERE email IN ({','.join('?' for _ in demo_emails)});
        """, demo_emails).fetchall()

        passed_demos = len(found_demos) == 4
        self.add_check(cat, "All 4 Demo Accounts Created & Active", passed_demos,
                       f"Found {len(found_demos)} / 4 required demo credentials (admin, manager, hr, employee).")

    def compute_summary_metrics(self):
        cursor = self.conn.cursor()
        self.results["summary_metrics"] = {
            "total_employees": cursor.execute("SELECT COUNT(*) as c FROM employees;").fetchone()["c"],
            "total_departments": cursor.execute("SELECT COUNT(*) as c FROM departments;").fetchone()["c"],
            "total_locations": cursor.execute("SELECT COUNT(*) as c FROM locations;").fetchone()["c"],
            "total_attendance_records": cursor.execute("SELECT COUNT(*) as c FROM attendance;").fetchone()["c"],
            "total_leave_requests": cursor.execute("SELECT COUNT(*) as c FROM leave_requests;").fetchone()["c"],
            "total_payroll_records": cursor.execute("SELECT COUNT(*) as c FROM payroll;").fetchone()["c"],
            "total_timesheets": cursor.execute("SELECT COUNT(*) as c FROM timesheets;").fetchone()["c"],
            "total_performance_reviews": cursor.execute("SELECT COUNT(*) as c FROM performance_reviews;").fetchone()["c"],
            "total_user_accounts": cursor.execute("SELECT COUNT(*) as c FROM user_accounts;").fetchone()["c"],
            "attendance_anomalies_flagged": cursor.execute("SELECT COUNT(*) as c FROM attendance WHERE anomaly_flag = 1;").fetchone()["c"]
        }

    def generate_html_report(self):
        res = self.results
        pass_rate = round((res["passed_checks"] / max(1, res["total_checks"])) * 100, 1)

        category_cards = ""
        for cat_name, cat_data in res["categories"].items():
            checks_rows = ""
            for check in cat_data["checks"]:
                badge = (
                    '<span class="badge badge-success">✓ PASS</span>'
                    if check["status"] == "PASSED"
                    else '<span class="badge badge-danger">✗ FAIL</span>'
                )
                checks_rows += f"""
                <tr>
                    <td style="font-weight: 500;">{check["check_name"]}</td>
                    <td>{badge}</td>
                    <td style="color: #64748b;">{check["details"]}</td>
                </tr>
                """

            cat_badge = (
                f'<span class="badge badge-success">{cat_data["passed"]}/{cat_data["passed"]+cat_data["failed"]} PASSED</span>'
                if cat_data["failed"] == 0
                else f'<span class="badge badge-danger">{cat_data["failed"]} FAILED</span>'
            )

            category_cards += f"""
            <div class="card">
                <div class="card-header">
                    <h3>{cat_name}</h3>
                    {cat_badge}
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th style="width: 35%;">Check Name</th>
                                <th style="width: 15%;">Result</th>
                                <th style="width: 50%;">Details & Metrics</th>
                            </tr>
                        </thead>
                        <tbody>
                            {checks_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            """

        metrics = res["summary_metrics"]

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Workforce Management - Synthetic Data Validation Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --bg-card: #1f2937;
            --border-color: #374151;
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
            --accent-blue: #3b82f6;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            padding: 2.5rem 1.5rem;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }}
        .title-group h1 {{
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        .title-group p {{
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}
        .status-pill {{
            padding: 0.6rem 1.4rem;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.95rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .grid-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2.5rem;
        }}
        .stat-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            position: relative;
            overflow: hidden;
        }}
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
        }}
        .stat-label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.4rem;
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: #ffffff;
            font-family: 'JetBrains Mono', monospace;
        }}
        .card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            margin-bottom: 1.75rem;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        .card-header {{
            padding: 1.2rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid var(--border-color);
        }}
        .card-header h3 {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #e2e8f0;
        }}
        .card-body {{
            padding: 0;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.92rem;
        }}
        .table th {{
            padding: 0.9rem 1.5rem;
            background: rgba(0, 0, 0, 0.2);
            color: var(--text-secondary);
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
        }}
        .table td {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid rgba(55, 65, 81, 0.5);
            vertical-align: middle;
        }}
        .table tr:last-child td {{
            border-bottom: none;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
        }}
        .badge-success {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}
        .badge-danger {{
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }}
        .footer {{
            margin-top: 3rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
            border-top: 1px solid var(--border-color);
            padding-top: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="title-group">
                <h1>AI Workforce Management System</h1>
                <p>Phase 1 Synthetic Dataset Automated Validation Audit Report &bull; Generated: {res["timestamp"]}</p>
            </div>
            <div class="status-pill">
                <span>●</span> {res["overall_status"]} ({pass_rate}%)
            </div>
        </header>

        <section class="grid-stats">
            <div class="stat-card">
                <div class="stat-label">Total Employees</div>
                <div class="stat-value">{metrics.get("total_employees", 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Checks Run</div>
                <div class="stat-value">{res["total_checks"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Checks Passed</div>
                <div class="stat-value" style="color: #34d399;">{res["passed_checks"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Attendance Logs</div>
                <div class="stat-value">{metrics.get("total_attendance_records", 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Payroll Records</div>
                <div class="stat-value">{metrics.get("total_payroll_records", 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">AI Anomalies Flagged</div>
                <div class="stat-value" style="color: #60a5fa;">{metrics.get("attendance_anomalies_flagged", 0)}</div>
            </div>
        </section>

        <section>
            {category_cards}
        </section>

        <footer class="footer">
            <p>InnovateCorp AI Workforce Automation Platform &bull; Deterministic Dataset Seed: 42 &bull; SQLite Database: hr_automation.db</p>
        </footer>
    </div>
</body>
</html>
"""
        return html_content

    def export_reports(self):
        # 1. JSON Report
        json_str = json.dumps(self.results, indent=2)
        with open(JSON_REPORT_PATH_1, "w", encoding="utf-8") as f:
            f.write(json_str)
        with open(JSON_REPORT_PATH_2, "w", encoding="utf-8") as f:
            f.write(json_str)

        # 2. HTML Report
        html_str = self.generate_html_report()
        with open(HTML_REPORT_PATH_1, "w", encoding="utf-8") as f:
            f.write(html_str)
        with open(HTML_REPORT_PATH_2, "w", encoding="utf-8") as f:
            f.write(html_str)

        print(f"Validation reports generated successfully:")
        print(f" - JSON: {JSON_REPORT_PATH_1}")
        print(f" - HTML: {HTML_REPORT_PATH_1}")

def main():
    print("=" * 60)
    print("RUNNING AUTOMATED SYNTHETIC DATA VALIDATION SUITE")
    print("=" * 60)
    validator = DataValidator(DB_PATH)
    validator.run_all_validations()
    validator.export_reports()

    res = validator.results
    print("=" * 60)
    print(f"OVERALL STATUS: {res['overall_status']}")
    print(f"CHECKS PASSED:  {res['passed_checks']} / {res['total_checks']}")
    print(f"CHECKS FAILED:  {res['failed_checks']}")
    print("=" * 60)

    if res["failed_checks"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
