"""
Live API Integration Verification Script
----------------------------------------
Performs real HTTP requests against the running FastAPI server at http://127.0.0.1:8000.
Tests public, authenticated, and role-scoped endpoints.
"""

import time
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_live_server():
    print("=" * 60)
    print("LIVE API INTEGRATION VERIFICATION")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    with httpx.Client(timeout=10.0) as client:
        # 1. Health check
        print("\n1. Testing GET /health...")
        res = client.get(f"{BASE_URL}/health")
        print(f"   Status: {res.status_code}")
        print(f"   Response: {res.json()}")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Authentication
        print("\n2. Testing POST /auth/login with HR Demo credentials...")
        res = client.post(f"{BASE_URL}/auth/login", json={"email": "hr@demo.com", "password": "Demo@2026"})
        print(f"   Status: {res.status_code}")
        assert res.status_code == 200
        hr_token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {hr_token}"}
        print("   JWT Access Token obtained successfully.")

        # 3. Employees
        print("\n3. Testing GET /employees (Page 1, 5 records)...")
        res = client.get(f"{BASE_URL}/employees?page=1&page_size=5", headers=headers)
        print(f"   Status: {res.status_code}")
        data = res.json()
        print(f"   Total Employees: {data['total']}, Returned: {len(data['data'])}")
        assert res.status_code == 200
        assert data["total"] == 200

        # 4. Departments
        print("\n4. Testing GET /departments...")
        res = client.get(f"{BASE_URL}/departments", headers=headers)
        print(f"   Status: {res.status_code}")
        depts = res.json()
        print(f"   Departments Count: {len(depts)}")
        assert res.status_code == 200
        assert len(depts) == 9

        # 5. Attendance
        print("\n5. Testing GET /attendance (recent records)...")
        res = client.get(f"{BASE_URL}/attendance?page=1&page_size=5", headers=headers)
        print(f"   Status: {res.status_code}")
        att = res.json()
        print(f"   Total Attendance Records: {att['total']:,}")
        assert res.status_code == 200
        assert att["total"] >= 24600

        # 6. Leave Requests
        print("\n6. Testing GET /leave/requests...")
        res = client.get(f"{BASE_URL}/leave/requests?page=1&page_size=5", headers=headers)
        print(f"   Status: {res.status_code}")
        lvr = res.json()
        print(f"   Total Leave Requests: {lvr['total']}")
        assert res.status_code == 200

        # 7. Shifts
        print("\n7. Testing GET /shifts...")
        res = client.get(f"{BASE_URL}/shifts", headers=headers)
        print(f"   Status: {res.status_code}")
        shifts = res.json()
        print(f"   Shifts Count: {len(shifts)}")
        assert res.status_code == 200
        assert len(shifts) == 4

        # 8. Timesheets
        print("\n8. Testing GET /timesheets...")
        res = client.get(f"{BASE_URL}/timesheets?page=1&page_size=5", headers=headers)
        print(f"   Status: {res.status_code}")
        ts = res.json()
        print(f"   Total Timesheets: {ts['total']}")
        assert res.status_code == 200

        # 9. Payroll Summary
        print("\n9. Testing GET /payroll/summary...")
        res = client.get(f"{BASE_URL}/payroll/summary?month=2026-03", headers=headers)
        print(f"   Status: {res.status_code}")
        pay = res.json()
        print(f"   Total Net Payroll Disbursement: INR {pay['total_net_disbursement']:,.2f}")
        assert res.status_code == 200

        # 10. Performance
        print("\n10. Testing GET /performance...")
        res = client.get(f"{BASE_URL}/performance", headers=headers)
        print(f"   Status: {res.status_code}")
        perf = res.json()
        print(f"   Reviews Count: {len(perf)}")
        assert res.status_code == 200

        # 11. HR Dashboard Summary
        print("\n11. Testing GET /hr/summary...")
        res = client.get(f"{BASE_URL}/hr/summary", headers=headers)
        print(f"   Status: {res.status_code}")
        hr_sum = res.json()
        print(f"   HR Summary Metrics: {hr_sum}")
        assert res.status_code == 200

    print("\n" + "=" * 60)
    print("ALL 11 LIVE API INTEGRATION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    test_live_server()
