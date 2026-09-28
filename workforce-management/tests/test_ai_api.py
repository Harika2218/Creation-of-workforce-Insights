"""
Tests for AI Workforce Intelligence REST API Endpoints & RBAC
--------------------------------------------------------------
Verifies authentication, RBAC constraints, self-service scoping,
and payload structures for all /api/v1/ai/* routes.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def login(email: str, password: str = "Demo@2026") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture(scope="module")
def admin_token():
    return login("admin@demo.com")

@pytest.fixture(scope="module")
def hr_token():
    return login("hr@demo.com")

@pytest.fixture(scope="module")
def manager_token():
    return login("manager@demo.com")

@pytest.fixture(scope="module")
def employee_token():
    return login("employee@demo.com")

def test_unauthenticated_ai_endpoints():
    res = client.get("/api/v1/ai/absenteeism")
    assert res.status_code == 401

    res = client.get("/api/v1/ai/attrition")
    assert res.status_code == 401

def test_hr_can_access_all_ai_endpoints(hr_token):
    headers = {"Authorization": f"Bearer {hr_token}"}

    endpoints = [
        "/api/v1/ai/absenteeism",
        "/api/v1/ai/attrition",
        "/api/v1/ai/attendance-anomalies",
        "/api/v1/ai/productivity",
        "/api/v1/ai/workforce-forecast",
        "/api/v1/ai/staffing-recommendations",
        "/api/v1/ai/skill-gaps",
        "/api/v1/ai/shift-recommendations",
        "/api/v1/ai/resource-recommendations",
        "/api/v1/ai/model-metrics",
    ]
    for ep in endpoints:
        res = client.get(ep, headers=headers)
        assert res.status_code == 200, f"Failed for {ep}: {res.text}"
        data = res.json()
        assert data is not None

def test_employee_self_scoping(employee_token):
    headers = {"Authorization": f"Bearer {employee_token}"}

    # Employee EMP050 accessing own absenteeism -> allowed (200)
    res = client.get("/api/v1/ai/absenteeism/EMP050", headers=headers)
    assert res.status_code == 200
    assert res.json()["employee_id"] == "EMP050"

    # Employee EMP050 accessing another employee's absenteeism -> Forbidden (403)
    res = client.get("/api/v1/ai/absenteeism/EMP001", headers=headers)
    assert res.status_code == 403
    err_msg = res.json().get("error") or res.json().get("detail") or ""
    assert "Forbidden" in err_msg

    # Employee EMP050 accessing own productivity -> allowed (200)
    res = client.get("/api/v1/ai/productivity/EMP050", headers=headers)
    assert res.status_code == 200
    assert res.json()["employee_id"] == "EMP050"

    # Employee EMP050 accessing another employee's productivity -> Forbidden (403)
    res = client.get("/api/v1/ai/productivity/EMP002", headers=headers)
    assert res.status_code == 403

    # Employee EMP050 accessing organizational workforce forecast -> Forbidden (403)
    res = client.get("/api/v1/ai/workforce-forecast", headers=headers)
    assert res.status_code == 403

def test_manager_team_access(manager_token):
    headers = {"Authorization": f"Bearer {manager_token}"}

    # Manager can access workforce forecast and team shift recommendations
    res = client.get("/api/v1/ai/workforce-forecast", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/ai/shift-recommendations", headers=headers)
    assert res.status_code == 200

    res = client.get("/api/v1/ai/skill-gaps", headers=headers)
    assert res.status_code == 200

def test_model_metrics_content(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.get("/api/v1/ai/model-metrics", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "fairness_safeguards" in data
    assert "gender" in data["fairness_safeguards"]["protected_attributes_excluded"]
    assert "models" in data
