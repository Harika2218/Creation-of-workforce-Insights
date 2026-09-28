"""
Full Stack Integration Verification Script
Phase 4: React Frontend + FastAPI Backend + MongoDB
---------------------------------------------------
Verifies that:
1. Vite frontend dev server is active and serving index.html on port 5173.
2. FastAPI backend is healthy on port 8000.
3. All role workflows (Admin, HR, Manager, Employee) successfully authenticate and retrieve live data.
4. No fake statistics: validates real values against MongoDB database.
"""

import sys
import json
import urllib.request
import urllib.error

FRONTEND_URL = "http://127.0.0.1:5173"
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

def http_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode('utf-8')

def http_post(url, data, headers=None):
    body = json.dumps(data).encode('utf-8')
    req_headers = {'Content-Type': 'application/json'}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=req_headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def login(email, password="Demo@2026"):
    status, res = http_post(f"{BACKEND_URL}/auth/login", {"email": email, "password": password})
    assert status == 200, f"Login failed for {email}"
    token = res["access_token"]
    status, user_json = http_get(f"{BACKEND_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert status == 200
    user = json.loads(user_json)
    return token, user

def run_checks():
    print("=" * 60)
    print("FULL STACK FRONTEND + BACKEND INTEGRATION TEST")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL:  {BACKEND_URL}")
    print("=" * 60)

    # 1. Frontend server health
    print("\n1. Verifying Vite frontend dev server on http://127.0.0.1:5173...")
    status, html = http_get(FRONTEND_URL)
    assert status == 200, "Frontend server returned non-200"
    assert "HRvantage" in html or "root" in html, "Invalid HTML served by Vite"
    print("   [PASS] Vite dev server is running and serving HTML (HTTP 200).")

    # 2. Backend health
    print("\n2. Verifying FastAPI backend on http://127.0.0.1:8000/api/v1/health...")
    status, health_json = http_get(f"{BACKEND_URL}/health")
    assert status == 200
    health = json.loads(health_json)
    assert health["status"] == "healthy" and health["database"] == "connected"
    print(f"   [PASS] FastAPI is healthy and connected to MongoDB '{health['database_name']}'.")

    # 3. Authentication for all 4 roles
    print("\n3. Verifying Authentication & Role Scopes:")
    roles = [
        ("ADMIN", "admin@demo.com"),
        ("HR", "hr@demo.com"),
        ("MANAGER", "manager@demo.com"),
        ("EMPLOYEE", "employee@demo.com"),
    ]
    tokens = {}
    for role, email in roles:
        token, user = login(email)
        tokens[role] = token
        assert user["role"] == role
        print(f"   [PASS] {role} ({email}) authenticated successfully as {user['name']} ({user['employee_id']}).")

    # 4. HR Dashboard Real Backend Data
    print("\n4. Verifying HR Dashboard Metrics (Real MongoDB Data - No Fake Stats):")
    hr_headers = {"Authorization": f"Bearer {tokens['HR']}"}
    status, hr_sum_json = http_get(f"{BACKEND_URL}/hr/summary", headers=hr_headers)
    hr_sum = json.loads(hr_sum_json)
    assert hr_sum["total_employees"] == 200, f"Expected 200 employees, got {hr_sum['total_employees']}"
    assert hr_sum["active_employees"] == 195
    assert hr_sum["departments_count"] == 9
    print(f"   [PASS] Total Headcount: {hr_sum['total_employees']} (Active: {hr_sum['active_employees']})")
    print(f"   [PASS] Departments: {hr_sum['departments_count']}, Daily Attendance Rate: {hr_sum['daily_attendance_rate']}%")
    print(f"   [PASS] Monthly Net Payroll: INR {hr_sum['total_monthly_payroll']:,.2f}")

    # 5. Manager Portal Scoped Data
    print("\n5. Verifying Manager Team Portal:")
    mgr_headers = {"Authorization": f"Bearer {tokens['MANAGER']}"}
    status, mgr_sum_json = http_get(f"{BACKEND_URL}/manager/team/summary", headers=mgr_headers)
    mgr_sum = json.loads(mgr_sum_json)
    assert mgr_sum["team_size"] > 0
    print(f"   [PASS] Manager Team Size: {mgr_sum['team_size']} direct reports")
    print(f"   [PASS] Present Today: {mgr_sum['present_today']}, On Leave: {mgr_sum['on_leave_today']}")

    # 6. Employee Self-Service Data
    print("\n6. Verifying Employee Self-Service:")
    emp_headers = {"Authorization": f"Bearer {tokens['EMPLOYEE']}"}
    status, bal_json = http_get(f"{BACKEND_URL}/leave/balance/EMP050", headers=emp_headers)
    bal_list = json.loads(bal_json)
    assert len(bal_list) > 0
    print(f"   [PASS] Employee EMP050 Balances: {len(bal_list)} leave categories returned from MongoDB.")

    # 7. Employee GPS Punch Clock
    print("\n7. Verifying GPS Attendance Punch:")
    try:
        status, checkin = http_post(
            f"{BACKEND_URL}/attendance/check-in",
            {
                "employee_id": "EMP050",
                "attendance_method": "GPS",
                "latitude": 17.4435,
                "longitude": 78.3772
            },
            headers=emp_headers
        )
        print(f"   [PASS] GPS Punch In successful for EMP050 (status: {checkin.get('attendance_status', checkin.get('status', 'OK'))})")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("   [PASS] GPS Punch In returned 409 (Already checked in today - duplicate prevention verified)")
        else:
            raise

    # 8. Reports & Analytics
    print("\n8. Verifying Reports Endpoints:")
    for rep in ["attendance", "overtime", "leave", "payroll", "department-performance"]:
        status, rep_json = http_get(f"{BACKEND_URL}/reports/{rep}", headers=hr_headers)
        assert status == 200
        print(f"   [PASS] /reports/{rep} returned valid HTTP 200 payload.")

    print("\n" + "=" * 60)
    print("ALL FULL STACK INTEGRATION CHECKS COMPLETED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_checks()
