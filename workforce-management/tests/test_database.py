"""
AI-Powered Workforce Management Automation System
Automated MongoDB Database Test Suite
--------------------------------------------------
Tests database connectivity, index enforcement, unique constraints,
relationship integrity, formula consistency, and seeder idempotency.
"""

import os
import sys
import pytest
from pymongo.errors import DuplicateKeyError

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from database.mongodb import get_db, check_connection
from database.seed_database import seed_database

@pytest.fixture(scope="module")
def db():
    conn = check_connection()
    assert conn["ok"], f"MongoDB connection failed: {conn.get('error')}"
    return get_db()

# 1. Connection & Ping
def test_mongodb_connection(db):
    conn_info = check_connection()
    assert conn_info["ok"] is True
    assert conn_info["status"] == "connected"
    assert db.name == "hr_automation"

# 2. Exactly 200 Employees (EMP001 to EMP200, no EMP201)
def test_exact_200_employees(db):
    count = db.employees.count_documents({})
    assert count == 200, f"Expected exactly 200 employees, found {count}"

    emp001 = db.employees.find_one({"employee_id": "EMP001"})
    assert emp001 is not None, "EMP001 (CEO) must exist"

    emp200 = db.employees.find_one({"employee_id": "EMP200"})
    assert emp200 is not None, "EMP200 must exist"

    emp201 = db.employees.find_one({"employee_id": "EMP201"})
    assert emp201 is None, "EMP201 must NOT exist"

# 3. Unique Index Enforcement on Employee ID
def test_duplicate_employee_id_prevention(db):
    duplicate_emp = {
        "employee_id": "EMP001",
        "first_name": "Duplicate",
        "last_name": "Test",
        "email": "duplicate.test@innovatecorp.demo",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "phone": "+91-9999999999",
        "address": "Test Address",
        "joining_date": "2022-01-01",
        "employment_type": "Full-Time",
        "designation": "Test",
        "department_id": "DEP01",
        "manager_id": "EMP001",
        "location_id": "LOC01",
        "salary": 1000000.0,
        "experience": 5.0,
        "employment_status": "Active",
        "role": "EMPLOYEE"
    }
    with pytest.raises(DuplicateKeyError):
        db.employees.insert_one(duplicate_emp)

# 4. Unique Index Enforcement on Employee Email
def test_duplicate_email_prevention(db):
    duplicate_email_emp = {
        "employee_id": "EMP999",
        "first_name": "Duplicate",
        "last_name": "Email",
        "email": "vikramaditya.singhania@innovatecorp.demo", # EMP001's email
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "phone": "+91-9999999999",
        "address": "Test Address",
        "joining_date": "2022-01-01",
        "employment_type": "Full-Time",
        "designation": "Test",
        "department_id": "DEP01",
        "manager_id": "EMP001",
        "location_id": "LOC01",
        "salary": 1000000.0,
        "experience": 5.0,
        "employment_status": "Active",
        "role": "EMPLOYEE"
    }
    with pytest.raises(DuplicateKeyError):
        db.employees.insert_one(duplicate_email_emp)

# 5. Relational Reference Integrity
def test_reference_integrity(db):
    valid_depts = set(db.departments.distinct("department_id"))
    valid_locs = set(db.locations.distinct("location_id"))
    valid_emps = set(db.employees.distinct("employee_id"))

    # Departments & Locations
    assert db.employees.count_documents({"department_id": {"$nin": list(valid_depts)}}) == 0
    assert db.employees.count_documents({"location_id": {"$nin": list(valid_locs)}}) == 0

    # No self-managed employees
    assert db.employees.count_documents({
        "$expr": {"$and": [{"$ne": ["$manager_id", None]}, {"$eq": ["$manager_id", "$employee_id"]}]}
    }) == 0

    # Managers exist
    assert db.employees.count_documents({
        "$and": [{"manager_id": {"$ne": None}}, {"manager_id": {"$nin": list(valid_emps)}}]
    }) == 0

# 6. Attendance Integrity & Anomaly Cataloging
def test_attendance_integrity(db):
    att_count = db.attendance.count_documents({})
    assert att_count >= 24600, f"Expected at least 24,600 attendance logs, found {att_count}"

    # Check-out later than check-in for non-night shifts
    invalid_checkout = db.attendance.count_documents({
        "check_in": {"$ne": None},
        "check_out": {"$ne": None},
        "shift_id": {"$ne": "SH04"},
        "$expr": {"$lte": ["$check_out", "$check_in"]}
    })
    assert invalid_checkout == 0, f"Found {invalid_checkout} invalid checkouts"

    # Anomaly catalog
    flagged = db.attendance.count_documents({"anomaly_flag": 1})
    anomaly_docs = db.attendance_anomalies.count_documents({})
    assert flagged == anomaly_docs, "Anomaly catalog count mismatch"

# 7. Leave Balances Consistency
def test_leave_balances(db):
    mismatches = db.leave_balances.count_documents({
        "$expr": {
            "$gt": [
                {"$abs": {"$subtract": [{"$add": ["$used_days", "$remaining_days"]}, "$allocated_days"]}},
                0.05
            ]
        }
    })
    assert mismatches == 0, f"Found {mismatches} mismatched leave balances"

# 8. Payroll Mathematical Accuracy
def test_payroll_math_and_non_negative(db):
    payroll_count = db.payroll_records.count_documents({})
    assert payroll_count == 1200, f"Expected 1,200 payroll records, found {payroll_count}"

    # Gross formula
    gross_discrepancies = db.payroll_records.count_documents({
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
    assert gross_discrepancies == 0, f"Found {gross_discrepancies} gross salary calculation errors"

    # Net formula
    net_discrepancies = db.payroll_records.count_documents({
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
    assert net_discrepancies == 0, f"Found {net_discrepancies} net salary calculation errors"

    # Non-negative
    negative_salaries = db.payroll_records.count_documents({"net_salary": {"$lte": 0}})
    assert negative_salaries == 0, f"Found {negative_salaries} non-positive net salaries"

# 9. Timesheets Bounds & Formula
def test_timesheet_integrity(db):
    ts_count = db.timesheets.count_documents({})
    assert ts_count >= 4000, f"Expected at least 4,000 timesheets, found {ts_count}"

    mismatches = db.timesheets.count_documents({
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
    assert mismatches == 0, f"Found {mismatches} timesheet hour discrepancies"

    out_of_bounds = db.timesheets.count_documents({
        "$or": [{"hours_worked": {"$lte": 0}}, {"hours_worked": {"$gt": 24}}]
    })
    assert out_of_bounds == 0, f"Found {out_of_bounds} out-of-bounds timesheets"

# 10. Seeder Idempotency Test
def test_seeder_idempotency(db):
    # Run seed again
    seed_database()
    emp_count = db.employees.count_documents({})
    assert emp_count == 200, f"Employee count altered after re-seeding! Expected 200, got {emp_count}"
    payroll_count = db.payroll_records.count_documents({})
    assert payroll_count == 1200, f"Payroll records duplicated! Expected 1200, got {payroll_count}"
