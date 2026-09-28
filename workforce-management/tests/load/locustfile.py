"""
AI-Powered Workforce Management Automation System
Locust Load & Stress Testing Scenario
--------------------------------------------------
Usage:
    locust -f tests/load/locustfile.py --headless -u 20 -r 5 --run-time 1m --host http://localhost:8000
"""

from locust import HttpUser, task, between

class EnterpriseWorkforceUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Authenticates a synthetic employee user on session launch."""
        res = self.client.post("/api/v1/auth/login", json={
            "email": "employee@demo.com",
            "password": "Demo@2026"
        })
        if res.status_code == 200:
            token = res.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(4)
    def check_liveness_and_readiness(self):
        self.client.get("/api/v1/health/live")
        self.client.get("/api/v1/health/ready")

    @task(3)
    def view_dashboard_and_notifications(self):
        self.client.get("/api/v1/notifications?limit=10", headers=self.headers)
        self.client.get("/api/v1/attendance/today", headers=self.headers)

    @task(2)
    def view_shift_and_leaves(self):
        self.client.get("/api/v1/shifts/my", headers=self.headers)
        self.client.get("/api/v1/leave/balances", headers=self.headers)

    @task(1)
    def query_ai_attrition_risk(self):
        self.client.post(
            "/api/v1/ai/attrition/predict",
            json={"employee_id": "EMP004"},
            headers=self.headers
        )
