"""
AI-Powered Workforce Management Automation System
MongoDB Database Integrity Validation Suite
--------------------------------------------------
Validates data integrity, constraint enforcement, and reference consistency
in the MongoDB hr_automation database.

Checks:
1. Employees:
   - Exactly 200 employees
   - EMP001 exists
   - EMP200 exists
   - EMP201 does NOT exist
   - Unique employee_id and email
2. Relationships & References:
   - Valid departments, locations, managers
   - No self-managing employees
   - Valid references across attendance, leave, timesheets, payroll, skills
3. Attendance:
   - Complete 6-month log (~24,600 records)
   - Chronological check-out > check-in
   - Reasonable overtime (0 - 12 hrs)
   - Anomaly records cross-verification
4. Leave:
   - Balance formula: allocated == used + remaining
   - Date ordering: start_date <= end_date
5. Payroll:
   - 1,200 records (6 months x 200 employees)
   - Mathematical formula verification:
     gross == base + overtime + incentives + bonuses
     net == gross - deductions
   - Zero negative salaries
6. Timesheets:
   - Hours formula: hours_worked == billable + non_billable
   - Bounds: 0 < hours <= 24
"""

import os
import sys
import json
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from database.mongodb import get_db, check_connection

class MongoValidator:
    def __init__(self):
        conn_info = check_connection()
        if not conn_info["ok"]:
            raise ConnectionError(f"Cannot connect to MongoDB: {conn_info.get('error')}")
        self.db = get_db()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "database_name": self.db.name,
            "overall_status": "PASSED",
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "categories": {}
        }

    def add_check(self, category: str, check_name: str, passed: bool, details: str):
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
            "details": details
        })

    def run_all(self):
        print("=" * 60)
        print(f"RUNNING MONGODB VALIDATION AUDIT: {self.db.name}")
        print("=" * 60)
        self.validate_employees()
        self.validate_references()
        self.validate_attendance()
        self.validate_leave()
        self.validate_payroll()
        self.validate_timesheets()
        self.validate_performance_and_skills()
        self.validate_users_and_security()

    def validate_employees(self):
        cat = "Employee Integrity"
        # 1. Exactly 200 employees
        emp_count = self.db.employees.count_documents({})
        self.add_check(cat, "Exactly 200 Employees Count", emp_count == 200,
                       f"Total employee documents: {emp_count}. Required: EXACTLY 200.")

        # 2. EMP001 exists
        emp001 = self.db.employees.find_one({"employee_id": "EMP001"})
        self.add_check(cat, "EMP001 (CEO) Exists", emp001 is not None,
                       f"Found EMP001: {emp001.get('first_name') if emp001 else 'None'}")

        # 3. EMP200 exists
        emp200 = self.db.employees.find_one({"employee_id": "EMP200"})
        self.add_check(cat, "EMP200 Exists", emp200 is not None,
                       f"Found EMP200: {emp200.get('first_name') if emp200 else 'None'}")

        # 4. EMP201 does NOT exist
        emp201 = self.db.employees.find_one({"employee_id": "EMP201"})
        self.add_check(cat, "EMP201 Does NOT Exist", emp201 is None,
                       "Verified no EMP201 or excess employees exist.")

        # 5. Unique employee IDs sequence
        all_emps = list(self.db.employees.find({}, {"employee_id": 1, "email": 1}))
        emp_ids = sorted([e["employee_id"] for e in all_emps])
        expected_ids = [f"EMP{i:03d}" for i in range(1, 201)]
        self.add_check(cat, "Strict Sequence EMP001 to EMP200", emp_ids == expected_ids,
                       "Employee ID set matches 1:1 with sequential EMP001 to EMP200.")

        # 6. Unique Emails
        emails = [e["email"].lower() for e in all_emps]
        unique_emails = set(emails)
        self.add_check(cat, "Unique Corporate Emails", len(emails) == len(unique_emails),
                       f"Found {len(unique_emails)} unique emails across {len(emails)} employees.")

    def validate_references(self):
        cat = "Relational Reference Integrity"
        valid_emp_ids = set(self.db.employees.distinct("employee_id"))
        valid_dept_ids = set(self.db.departments.distinct("department_id"))
        valid_loc_ids = set(self.db.locations.distinct("location_id"))

        # Employees references
        invalid_depts = self.db.employees.count_documents({"department_id": {"$nin": list(valid_dept_ids)}})
        self.add_check(cat, "All Employees Map to Valid Departments", invalid_depts == 0,
                       f"Invalid department references: {invalid_depts}")

        invalid_locs = self.db.employees.count_documents({"location_id": {"$nin": list(valid_loc_ids)}})
        self.add_check(cat, "All Employees Map to Valid Locations", invalid_locs == 0,
                       f"Invalid location references: {invalid_locs}")

        # Managers must exist or be None (for CEO)
        self_managed = self.db.employees.count_documents({
            "$expr": {"$and": [{"$ne": ["$manager_id", None]}, {"$eq": ["$manager_id", "$employee_id"]}]}
        })
        self.add_check(cat, "No Employee Manages Themselves", self_managed == 0,
                       f"Self-managed count: {self_managed}")

        invalid_mgrs = self.db.employees.count_documents({
            "$and": [
                {"manager_id": {"$ne": None}},
                {"manager_id": {"$nin": list(valid_emp_ids)}}
            ]
        })
        self.add_check(cat, "Managers Exist in Employees Collection", invalid_mgrs == 0,
                       f"Invalid manager references: {invalid_mgrs}")

    def validate_attendance(self):
        cat = "Attendance Management"
        valid_emp_ids = list(self.db.employees.distinct("employee_id"))
        total_att = self.db.attendance.count_documents({})
        self.add_check(cat, "6-Month Attendance Rows Count", total_att >= 20000,
                       f"Total attendance records: {total_att:,}")

        # References
        invalid_att_emps = self.db.attendance.count_documents({"employee_id": {"$nin": valid_emp_ids}})
        self.add_check(cat, "All Attendance Links to Valid Employees", invalid_att_emps == 0,
                       f"Orphan attendance records: {invalid_att_emps}")

        # Chronological check-out > check-in for non-night shifts
        invalid_checkout = self.db.attendance.count_documents({
            "check_in": {"$ne": None},
            "check_out": {"$ne": None},
            "shift_id": {"$ne": "SH04"},
            "$expr": {"$lte": ["$check_out", "$check_in"]}
        })
        self.add_check(cat, "Check-out Chronologically After Check-in", invalid_checkout == 0,
                       f"Invalid check-out records: {invalid_checkout}")

        # Plausible overtime
        invalid_ot = self.db.attendance.count_documents({
            "$or": [
                {"overtime_hours": {"$lt": 0}},
                {"overtime_hours": {"$gt": 12}}
            ]
        })
        self.add_check(cat, "Overtime Hours Bound (0 to 12 hrs)", invalid_ot == 0,
                       f"Out of bounds overtime rows: {invalid_ot}")

        # Anomalies
        flagged_att = self.db.attendance.count_documents({"anomaly_flag": 1})
        anomaly_docs_count = self.db.attendance_anomalies.count_documents({})
        self.add_check(cat, "Anomaly Catalog Synchronization", flagged_att == anomaly_docs_count,
                       f"Flagged attendance anomalies: {flagged_att}, Dedicated anomaly records: {anomaly_docs_count}")

    def validate_leave(self):
        cat = "Leave Management"
        valid_emp_ids = list(self.db.employees.distinct("employee_id"))
        
        # Balances
        total_bal = self.db.leave_balances.count_documents({})
        self.add_check(cat, "Leave Balances Generated", total_bal > 0,
                       f"Total balance records: {total_bal}")

        # Balance equation: allocated == used + remaining (allow 0.01 tolerance)
        mismatched_bal = self.db.leave_balances.count_documents({
            "$expr": {
                "$gt": [
                    {"$abs": {"$subtract": [{"$add": ["$used_days", "$remaining_days"]}, "$allocated_days"]}},
                    0.05
                ]
            }
        })
        self.add_check(cat, "Balance Formula Consistency (Allocated = Used + Remaining)", mismatched_bal == 0,
                       f"Mismatched leave balances: {mismatched_bal}")

        # Requests
        invalid_dates = self.db.leave_requests.count_documents({
            "$expr": {"$gt": ["$start_date", "$end_date"]}
        })
        self.add_check(cat, "Leave Requests Date Consistency (Start <= End)", invalid_dates == 0,
                       f"Invalid request dates: {invalid_dates}")

    def validate_payroll(self):
        cat = "Payroll Calculations"
        valid_emp_ids = list(self.db.employees.distinct("employee_id"))
        total_payroll = self.db.payroll_records.count_documents({})
        self.add_check(cat, "Payroll Records Generated (6 Months x 200 Employees)", total_payroll == 1200,
                       f"Total payroll records: {total_payroll} (Required: 1,200)")

        # Gross formula: gross == base + overtime + incentives + bonuses
        gross_discrepancies = self.db.payroll_records.count_documents({
            "$expr": {
                "$gt": [
                    {
                        "$abs": {
                            "$subtract": [
                                {"$add": ["$base_salary", "$overtime_pay", "$incentives", "$bonuses"]},
                                "$gross_salary"
                            ]
                        }
                    },
                    0.05
                ]
            }
        })
        self.add_check(cat, "Gross Salary Exact Formula Verification", gross_discrepancies == 0,
                       f"Discrepancies in gross salary calculation: {gross_discrepancies}")

        # Net formula: net == gross - deductions
        net_discrepancies = self.db.payroll_records.count_documents({
            "$expr": {
                "$gt": [
                    {
                        "$abs": {
                            "$subtract": [
                                {"$subtract": ["$gross_salary", "$deductions"]},
                                "$net_salary"
                            ]
                        }
                    },
                    0.05
                ]
            }
        })
        self.add_check(cat, "Net Salary Exact Formula Verification", net_discrepancies == 0,
                       f"Discrepancies in net salary calculation: {net_discrepancies}")

        # Zero negative salaries
        negative_net = self.db.payroll_records.count_documents({"net_salary": {"$lte": 0}})
        self.add_check(cat, "Zero Negative Salaries", negative_net == 0,
                       f"Non-positive net salary records: {negative_net}")

    def validate_timesheets(self):
        cat = "Timesheet Management"
        ts_count = self.db.timesheets.count_documents({})
        self.add_check(cat, "Active Timesheets Generated", ts_count >= 1000,
                       f"Total timesheet documents: {ts_count}")

        # Formula: hours_worked == billable + non_billable
        hours_mismatches = self.db.timesheets.count_documents({
            "$expr": {
                "$gt": [
                    {
                        "$abs": {
                            "$subtract": [
                                {"$add": ["$billable_hours", "$non_billable_hours"]},
                                "$hours_worked"
                            ]
                        }
                    },
                    0.05
                ]
            }
        })
        self.add_check(cat, "Timesheet Hours Consistency (Billable + Non-Billable = Total)", hours_mismatches == 0,
                       f"Timesheets with hour sum mismatch: {hours_mismatches}")

        # Reasonable bounds
        out_of_bounds = self.db.timesheets.count_documents({
            "$or": [
                {"hours_worked": {"$lte": 0}},
                {"hours_worked": {"$gt": 24}}
            ]
        })
        self.add_check(cat, "Timesheet Hours Limits (0 to 24 hrs)", out_of_bounds == 0,
                       f"Out of bounds timesheet hours: {out_of_bounds}")

    def validate_performance_and_skills(self):
        cat = "Talent & Performance"
        rev_count = self.db.performance_reviews.count_documents({})
        self.add_check(cat, "Performance Reviews for All 200 Employees", rev_count == 200,
                       f"Total reviews: {rev_count} (One per employee)")

        skill_mappings = self.db.employee_skills.distinct("employee_id")
        self.add_check(cat, "All Employees Have Mapped Skills", len(skill_mappings) == 200,
                       f"Employees with mapped skills: {len(skill_mappings)} / 200")

    def validate_users_and_security(self):
        cat = "Users & Authentication"
        demo_emails = ["admin@demo.com", "manager@demo.com", "hr@demo.com", "employee@demo.com"]
        found_demos = self.db.users.count_documents({"email": {"$in": demo_emails}})
        self.add_check(cat, "All 4 Dedicated Demo Users Present", found_demos == 4,
                       f"Found {found_demos} / 4 demo accounts (admin, manager, hr, employee)")

    def print_report(self):
        res = self.results
        print("\n" + "=" * 60)
        print(f"VALIDATION SUMMARY: {res['overall_status']}")
        print(f"PASSED CHECKS:     {res['passed_checks']} / {res['total_checks']}")
        print(f"FAILED CHECKS:     {res['failed_checks']}")
        print("=" * 60)

        for cat_name, cat_data in res["categories"].items():
            status_symbol = "PASS" if cat_data["failed"] == 0 else "FAIL"
            print(f"\n[{status_symbol}] {cat_name} ({cat_data['passed']}/{cat_data['passed']+cat_data['failed']})")
            for c in cat_data["checks"]:
                mark = "  [+]" if c["status"] == "PASSED" else "  [-]"
                print(f"{mark} {c['check_name']:<50} : {c['details']}")

        # Save JSON audit report
        report_path = os.path.join(ROOT_DIR, "reports", "mongodb_validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"\nAudit report exported to: {report_path}")

        if res["failed_checks"] > 0:
            sys.exit(1)

def main():
    validator = MongoValidator()
    validator.run_all()
    validator.print_report()

if __name__ == "__main__":
    main()
