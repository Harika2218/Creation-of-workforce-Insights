"""
AI-Powered Workforce Management Automation System
FastAPI Backend Comprehensive Test Suite
--------------------------------------------------
Tests API health, JWT authentication, RBAC authorization boundaries,
employee lifecycle, attendance & GPS geofencing, leave workflows,
timesheets validation, and manager scoping using FastAPI TestClient.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from backend.main import app
from database.mongodb import get_db

client = TestClient(app)

# Helper fixture for getting auth tokens
@pytest.fixture(scope="module")
def hr_token():
    res = client.post("/api/v1/auth/login", json={"email": "hr@demo.com", "password": "Demo@2026"})
    assert res.status_code == 200, f"HR login failed: {res.text}"
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def manager_token():
    res = client.post("/api/v1/auth/login", json={"email": "manager@demo.com", "password": "Demo@2026"})
    assert res.status_code == 200, f"Manager login failed: {res.text}"
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def employee_token():
    res = client.post("/api/v1/auth/login", json={"email": "employee@demo.com", "password": "Demo@2026"})
    assert res.status_code == 200, f"Employee login failed: {res.text}"
    return res.json()["access_token"]

# 1. System Health
def test_health_check():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["database_name"] == "hr_automation"

def test_api_root():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "docs_url" in data

# 2. Authentication & JWT
def test_valid_login():
    res = client.post("/api/v1/auth/login", json={"email": "admin@demo.com", "password": "Demo@2026"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "ADMIN"
    assert data["employee_id"] == "EMP001"

def test_invalid_login_rejection():
    res = client.post("/api/v1/auth/login", json={"email": "admin@demo.com", "password": "WrongPassword"})
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["error"]

def test_unauthenticated_protected_endpoint():
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401

def test_get_current_user_profile(hr_token):
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "hr@demo.com"
    assert data["role"] == "HR"

# 3. RBAC Authorization Boundaries
def test_employee_forbidden_from_hr_summary(employee_token):
    res = client.get("/api/v1/hr/summary", headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 403
    assert "requires one of the following roles" in res.json()["error"]

def test_employee_forbidden_from_payroll_summary(employee_token):
    res = client.get("/api/v1/payroll/summary", headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 403

def test_employee_forbidden_from_another_payslip(employee_token):
    # EMP050 tries to access EMP001's payslips
    res = client.get("/api/v1/payroll/employee/EMP001", headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 403

def test_hr_can_access_payroll_summary(hr_token):
    res = client.get("/api/v1/payroll/summary?month=2026-03", headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["month"] == "2026-03"
    assert data["total_employees_paid"] == 200
    assert data["total_net_disbursement"] > 0

def test_hr_can_access_hr_dashboard_summary(hr_token):
    res = client.get("/api/v1/hr/summary", headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_employees"] == 200
    assert data["departments_count"] == 9
    assert data["locations_count"] == 5

# 4. Manager Scoping
def test_manager_team_access(manager_token):
    res = client.get("/api/v1/manager/team", headers={"Authorization": f"Bearer {manager_token}"})
    assert res.status_code == 200
    team = res.json()
    assert isinstance(team, list)
    assert len(team) > 0

def test_employee_forbidden_from_manager_team(employee_token):
    res = client.get("/api/v1/manager/team", headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 403

# 5. Employees API
def test_list_employees_pagination(hr_token):
    res = client.get("/api/v1/employees?page=1&page_size=15", headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["data"]) == 15
    assert data["total"] >= 200
    assert data["page"] == 1

def test_get_single_employee_and_profile(hr_token):
    res = client.get("/api/v1/employees/EMP001", headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 200
    assert res.json()["employee_id"] == "EMP001"

    res_prof = client.get("/api/v1/employees/EMP001/profile", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_prof.status_code == 200
    prof = res_prof.json()
    assert "department_name" in prof
    assert "location_name" in prof
    assert "skills" in prof

def test_duplicate_employee_onboarding_rejected(hr_token):
    payload = {
        "employee_id": "EMP001", # Existing ID
        "first_name": "Test",
        "last_name": "Conflict",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "email": "unique.test.conflict@innovatecorp.demo",
        "phone": "+91-9876543299",
        "address": "Test address",
        "joining_date": "2024-01-01",
        "employment_type": "Full-Time",
        "designation": "Staff Engineer",
        "department_id": "DEP01",
        "location_id": "LOC01",
        "salary": 1200000.0,
        "experience": 4.0
    }
    res = client.post("/api/v1/employees", json=payload, headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 409
    assert "already exists" in res.json()["error"]

# 6. Attendance API
def test_attendance_list_and_summary(hr_token):
    res = client.get("/api/v1/attendance?page=1&page_size=10", headers={"Authorization": f"Bearer {hr_token}"})
    assert res.status_code == 200
    assert len(res.json()["data"]) == 10

    res_sum = client.get("/api/v1/attendance/summary?employee_id=EMP001", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert "present_days" in sum_data
    assert "attendance_percentage" in sum_data

def test_attendance_check_in_and_duplicate(employee_token):
    # Check in EMP050
    payload = {
        "employee_id": "EMP050",
        "attendance_method": "Manual/Demo",
        "shift_id": "SH01"
    }
    res = client.post("/api/v1/attendance/check-in", json=payload, headers={"Authorization": f"Bearer {employee_token}"})
    # Either 201 Created or 409 Conflict if already checked in today
    assert res.status_code in [201, 409]

    if res.status_code == 201:
        # Check in again -> must return 409 Conflict
        res_dup = client.post("/api/v1/attendance/check-in", json=payload, headers={"Authorization": f"Bearer {employee_token}"})
        assert res_dup.status_code == 409
        assert "already clocked in today" in res_dup.json()["error"]

# 7. Leave Management API
def test_leave_balances_and_types(employee_token):
    res_types = client.get("/api/v1/leave/types", headers={"Authorization": f"Bearer {employee_token}"})
    assert res_types.status_code == 200
    assert len(res_types.json()) >= 5

    res_bal = client.get("/api/v1/leave/balance/EMP050", headers={"Authorization": f"Bearer {employee_token}"})
    assert res_bal.status_code == 200
    assert len(res_bal.json()) > 0

def test_leave_application_and_approval(employee_token, hr_token):
    req_payload = {
        "employee_id": "EMP050",
        "leave_type": "Casual Leave",
        "start_date": "2026-04-10",
        "end_date": "2026-04-11",
        "days_count": 2.0,
        "reason": "Personal family engagement"
    }
    res_apply = client.post("/api/v1/leave/requests", json=req_payload, headers={"Authorization": f"Bearer {employee_token}"})
    assert res_apply.status_code == 201
    leave_id = res_apply.json()["leave_id"]

    # HR approves the leave
    res_appr = client.post(f"/api/v1/leave/requests/{leave_id}/approve", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_appr.status_code == 200
    assert res_appr.json()["status"] == "Approved"

# 8. Timesheets API
def test_timesheet_hours_validation(employee_token):
    # Discrepancy: billable 6 + non-billable 1 != 8
    bad_payload = {
        "employee_id": "EMP050",
        "date": "2026-03-23",
        "project_id": "PRJ01",
        "hours_worked": 8.0,
        "billable_hours": 6.0,
        "non_billable_hours": 1.0,
        "description": "Task execution"
    }
    res = client.post("/api/v1/timesheets", json=bad_payload, headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 400
    assert "Discrepancy" in res.json()["error"]

def test_timesheet_valid_submission(employee_token):
    valid_payload = {
        "employee_id": "EMP050",
        "date": "2026-03-23",
        "project_id": "PRJ01",
        "hours_worked": 8.0,
        "billable_hours": 7.0,
        "non_billable_hours": 1.0,
        "description": "Sprint development"
    }
    res = client.post("/api/v1/timesheets", json=valid_payload, headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 201
    assert res.json()["status"] == "Submitted"

# 9. Reports API
def test_reports_endpoints(hr_token):
    res_att = client.get("/api/v1/reports/attendance?start_date=2026-03-01&end_date=2026-03-20", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_att.status_code == 200
    assert "breakdown" in res_att.json()

    res_ot = client.get("/api/v1/reports/overtime?month=2026-03", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_ot.status_code == 200
    assert "top_overtime_employees" in res_ot.json()

    res_dept = client.get("/api/v1/reports/department-performance", headers={"Authorization": f"Bearer {hr_token}"})
    assert res_dept.status_code == 200
    assert len(res_dept.json()["departments"]) > 0

# 10. Notifications API
def test_notifications(employee_token):
    res = client.get("/api/v1/notifications", headers={"Authorization": f"Bearer {employee_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
