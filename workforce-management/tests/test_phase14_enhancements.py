"""
Phase 14 Advanced Enterprise Enhancements Test Suite
---------------------------------------------------
Verifies Multi-Location, Advanced Geofencing, Contractor Workforce,
Skills Intelligence, Workforce Simulation, Compliance Alerts, and Executive Analytics.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.mongodb import get_db

client = TestClient(app)

# Helper to get auth header
def get_auth_token(email: str = "admin@demo.com", password: str = "Demo@2026") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]

# -------------------------------------------------------------------
# 1. Multi-Location Workforce Tests
# -------------------------------------------------------------------
def test_list_locations():
    token = get_auth_token()
    res = client.get("/api/v1/locations", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    loc_ids = [l["location_id"] for l in data]
    assert "LOC01" in loc_ids
    assert "LOC02" in loc_ids
    assert data[0]["employee_count"] >= 0

def test_location_details_and_subresources():
    token = get_auth_token()
    res = client.get("/api/v1/locations/LOC01", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["location_id"] == "LOC01"
    assert "departments" in data
    assert "holidays_count" in data

    # Employees at location
    res_emp = client.get("/api/v1/locations/LOC01/employees", headers={"Authorization": f"Bearer {token}"})
    assert res_emp.status_code == 200
    assert "employees" in res_emp.json()

    # Holidays at location
    res_hol = client.get("/api/v1/locations/LOC01/holidays", headers={"Authorization": f"Bearer {token}"})
    assert res_hol.status_code == 200
    assert "holidays" in res_hol.json()

def test_location_geofence_update_rbac():
    emp_token = get_auth_token(email="employee@demo.com")
    admin_token = get_auth_token(email="admin@demo.com")

    payload = {"latitude": 17.4435, "longitude": 78.3772, "geofence_radius_meters": 600.0}

    # Employee must be rejected (403)
    res_emp = client.put("/api/v1/locations/LOC01/geofence", json=payload, headers={"Authorization": f"Bearer {emp_token}"})
    assert res_emp.status_code == 403

    # Admin must be allowed (200)
    res_admin = client.put("/api/v1/locations/LOC01/geofence", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert res_admin.json()["geofence_radius_meters"] == 600.0

# -------------------------------------------------------------------
# 2. Contractor & Vendor Workforce Tests
# -------------------------------------------------------------------
def test_contractor_workforce_lifecycle():
    token = get_auth_token(email="admin@demo.com")

    # List contractors
    res_list = client.get("/api/v1/contractors", headers={"Authorization": f"Bearer {token}"})
    assert res_list.status_code == 200
    contractors = res_list.json()
    assert len(contractors) >= 1
    assert "vendor_org" in contractors[0]

    # Get single contractor
    cid = contractors[0]["contractor_id"]
    res_c = client.get(f"/api/v1/contractors/{cid}", headers={"Authorization": f"Bearer {token}"})
    assert res_c.status_code == 200
    assert res_c.json()["contractor_id"] == cid

    # Submit contractor timesheet
    ts_payload = {
        "week_start_date": "2026-09-21",
        "hours_worked": 40.0,
        "task_description": "Cloud infrastructure optimization deliverables"
    }
    res_ts = client.post(f"/api/v1/contractors/{cid}/timesheets", json=ts_payload, headers={"Authorization": f"Bearer {token}"})
    assert res_ts.status_code == 201
    ts_data = res_ts.json()
    assert ts_data["hours_worked"] == 40.0
    assert ts_data["total_amount"] > 0
    assert ts_data["status"] == "Submitted"

    # Approve contractor timesheet
    ts_id = ts_data["timesheet_id"]
    res_app = client.put(f"/api/v1/contractors/timesheets/{ts_id}/approve", headers={"Authorization": f"Bearer {token}"})
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "Approved"

def test_contractor_does_not_inflate_regular_employees():
    """Verify exact 200 regular employee invariant is preserved."""
    db = get_db()
    assert db.employees.count_documents({}) == 200

# -------------------------------------------------------------------
# 3. Skills Intelligence & Training Recommendations Tests
# -------------------------------------------------------------------
def test_skill_gap_analysis():
    token = get_auth_token(email="admin@demo.com")
    res = client.get("/api/v1/skills/gap-analysis/EMP001", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["employee_id"] == "EMP001"
    assert "overall_readiness_pct" in data
    assert "skill_gaps" in data
    assert isinstance(data["skill_gaps"], list)

def test_training_recommendations_explainability():
    token = get_auth_token(email="admin@demo.com")
    res = client.get("/api/v1/training/recommendations/EMP001", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["employee_id"] == "EMP001"
    assert len(data["recommendations"]) > 0
    rec = data["recommendations"][0]
    assert "reason" in rec
    assert "expected_improvement" in rec
    assert "disclaimer" in rec
    assert "does not guarantee" in rec["disclaimer"].lower()

# -------------------------------------------------------------------
# 4. Workforce Scenario Simulation Tests
# -------------------------------------------------------------------
def test_workforce_simulation_engine():
    token = get_auth_token(email="admin@demo.com")

    # Scenario A: Demand Surge
    payload_a = {
        "scenario_type": "DEMAND_INCREASE",
        "percentage_change": 20.0,
        "department_id": None
    }
    res_a = client.post("/api/v1/ai/simulation", json=payload_a, headers={"Authorization": f"Bearer {token}"})
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["base_headcount"] == 200
    assert data_a["staffing_gap"] > 0
    assert data_a["projected_monthly_cost_delta"] > 0
    assert "Scenario Simulation" in data_a["label"]

    # Scenario B: Workforce Reduction
    payload_b = {
        "scenario_type": "WORKFORCE_REDUCTION",
        "percentage_change": 10.0
    }
    res_b = client.post("/api/v1/ai/simulation", json=payload_b, headers={"Authorization": f"Bearer {token}"})
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["staffing_gap"] < 0
    assert data_b["projected_monthly_cost_delta"] < 0

def test_workforce_simulation_rbac():
    emp_token = get_auth_token(email="employee@demo.com")
    payload = {"scenario_type": "DEMAND_INCREASE", "percentage_change": 15.0}
    res = client.post("/api/v1/ai/simulation", json=payload, headers={"Authorization": f"Bearer {emp_token}"})
    assert res.status_code == 403

# -------------------------------------------------------------------
# 5. Compliance Alerting Engine Tests
# -------------------------------------------------------------------
def test_compliance_alerts_engine():
    token = get_auth_token(email="admin@demo.com")
    res = client.get("/api/v1/compliance/alerts", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_active_alerts" in data
    assert "category_breakdown" in data
    assert "disclaimer" in data
    assert len(data["alerts"]) > 0

def test_compliance_alert_status_update():
    token = get_auth_token(email="admin@demo.com")
    res = client.get("/api/v1/compliance/alerts", headers={"Authorization": f"Bearer {token}"})
    alerts = res.json()["alerts"]
    if alerts:
        aid = alerts[0]["alert_id"]
        update_payload = {"status": "In_Review", "review_notes": "Manager scheduled 1-on-1 workload review."}
        res_up = client.put(f"/api/v1/compliance/alerts/{aid}/status", json=update_payload, headers={"Authorization": f"Bearer {token}"})
        assert res_up.status_code == 200
        assert res_up.json()["status"] == "In_Review"

# -------------------------------------------------------------------
# 6. Executive Workforce Overview Tests
# -------------------------------------------------------------------
def test_executive_workforce_summary():
    token = get_auth_token(email="admin@demo.com")
    res = client.get("/api/v1/hr/executive-summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["workforce_composition"]["regular_employees"] == 200
    assert "location_distribution" in data
    assert len(data["location_distribution"]) >= 1
    assert "financial_summary" in data
    assert data["financial_summary"]["total_workforce_spend"] > 0
    assert "operational_health" in data
