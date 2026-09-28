"""
Phase 10: External Integrations & Enterprise Connectivity Comprehensive Test Suite
----------------------------------------------------------------------------------
Verifies:
1. Integration registry discovery & RBAC access boundaries (Admin only).
2. Integration health introspection & safe non-destructive connection testing.
3. Feature flag enforcement (disabled by default, no crashes, no fake connections).
4. Circuit breaker & fault isolation (prevents external outages from halting platform).
5. Transient failure retry mechanism with exponential backoff.
6. Data synchronization engine & MongoDB sync audit logging.
7. Cryptographic webhook signature verification (HMAC-SHA256) & replay protection.
8. Biometric punch processing, pin-to-employee mapping, and deduplication.
9. Server-side GPS geofencing & anti-spoofing distance verification.
10. Strict 200 employee database invariant preservation.
"""

import time
import json
import hmac
import hashlib
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import settings
from database.mongodb import get_db
from backend.integrations.registry import registry
from backend.integrations.base.circuit_breaker import CircuitBreaker
from backend.integrations.base.exceptions import CircuitBreakerOpenError
from backend.integrations.base.retry import with_retry
from backend.integrations.geofence.validator import GeofenceValidator, calculate_haversine_distance
from backend.integrations.webhooks import WebhookSecurity, WebhookDispatcher

client = TestClient(app)

@pytest.fixture(scope="module")
def tokens():
    accounts = {
        "ADMIN": ("admin@demo.com", "Demo@2026"),
        "HR": ("hr@demo.com", "Demo@2026"),
        "EMPLOYEE": ("employee@demo.com", "Demo@2026")
    }
    toks = {}
    for role, (email, pwd) in accounts.items():
        res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        assert res.status_code == 200
        toks[role] = res.json()["access_token"]
    return toks


# ===================================================================
# 1. Integration Registry & Admin RBAC Boundaries
# ===================================================================
def test_integrations_list_admin_only(tokens):
    """Admin can list integrations; employees and unauthenticated calls are rejected."""
    # 1. Unauthenticated -> 401
    res = client.get("/api/v1/integrations")
    assert res.status_code == 401

    # 2. Employee role -> 403 Forbidden
    emp_res = client.get("/api/v1/integrations", headers={"Authorization": f"Bearer {tokens['EMPLOYEE']}"})
    assert emp_res.status_code == 403

    # 3. Admin role -> 200 OK with all registered enterprise connectors
    admin_res = client.get("/api/v1/integrations", headers={"Authorization": f"Bearer {tokens['ADMIN']}"})
    assert admin_res.status_code == 200
    integrations = admin_res.json()
    assert isinstance(integrations, list)
    assert len(integrations) >= 10

    names = {i["name"] for i in integrations}
    assert "email" in names
    assert "teams" in names
    assert "slack" in names
    assert "outlook_calendar" in names
    assert "google_calendar" in names
    assert "entra_id" in names
    assert "payroll_gateway" in names
    assert "sap" in names
    assert "oracle_hrms" in names
    assert "biometric" in names


# ===================================================================
# 2. Single Integration Health & Non-Existent Handlers
# ===================================================================
def test_integration_get_single_and_health(tokens):
    """Verifies detailed health introspection for specific connectors."""
    admin_headers = {"Authorization": f"Bearer {tokens['ADMIN']}"}

    # Valid integration: email
    res = client.get("/api/v1/integrations/email", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "email"
    assert "status" in data
    assert "circuit_breaker_state" in data

    # Non-existent integration -> 404
    missing_res = client.get("/api/v1/integrations/non_existent_tool", headers=admin_headers)
    assert missing_res.status_code == 404


# ===================================================================
# 3. Safe Test Connection (No Data Mutation)
# ===================================================================
def test_integration_test_connection_safe(tokens):
    """Executes safe connectivity verification across connectors."""
    admin_headers = {"Authorization": f"Bearer {tokens['ADMIN']}"}

    # 1. Email test connection
    res = client.post("/api/v1/integrations/email/test", headers=admin_headers)
    assert res.status_code == 200
    email_data = res.json()
    assert "status" in email_data
    assert "latency_ms" in email_data

    # 2. SAP ERP test connection (Honest status: DISABLED or BLOCKED_EXTERNAL_DEPENDENCY)
    sap_res = client.post("/api/v1/integrations/sap/test", headers=admin_headers)
    assert sap_res.status_code == 200
    sap_data = sap_res.json()
    assert sap_data["status"] in ["DISABLED", "NOT_CONFIGURED", "BLOCKED_EXTERNAL_DEPENDENCY"]
    assert sap_data["success"] is False  # Must not claim fake success!

    # 3. Biometric test connection
    bio_res = client.post("/api/v1/integrations/biometric/test", headers=admin_headers)
    assert bio_res.status_code == 200
    assert bio_res.json()["status"] in ["DISABLED", "NOT_CONFIGURED", "BLOCKED_EXTERNAL_DEPENDENCY"]


# ===================================================================
# 4. Circuit Breaker & Failure Isolation
# ===================================================================
def test_circuit_breaker_failure_isolation():
    """Verifies that circuit breaker isolates persistent external errors."""
    cb = CircuitBreaker(name="test_breaker", failure_threshold=3, recovery_timeout=0.2)

    def failing_remote_call():
        raise ConnectionResetError("Remote API dropped connection")

    # Fail 1
    with pytest.raises(ConnectionResetError):
        cb.call(failing_remote_call)
    assert cb.state == "CLOSED"

    # Fail 2
    with pytest.raises(ConnectionResetError):
        cb.call(failing_remote_call)
    assert cb.state == "CLOSED"

    # Fail 3 -> Trips to OPEN
    with pytest.raises(ConnectionResetError):
        cb.call(failing_remote_call)
    assert cb.state == "OPEN"

    # Subsequent call is short-circuited immediately without executing function
    with pytest.raises(CircuitBreakerOpenError):
        cb.call(failing_remote_call)

    # After recovery timeout elapses, transitions to HALF_OPEN
    time.sleep(0.25)
    with pytest.raises(ConnectionResetError):
        cb.call(failing_remote_call)

    # Manual reset returns to CLOSED
    cb.reset()
    assert cb.state == "CLOSED"


# ===================================================================
# 5. Retry Mechanism with Exponential Backoff
# ===================================================================
def test_retry_mechanism():
    """Verifies retry decorator recovers from transient errors."""
    attempts = 0

    @with_retry(max_retries=3, base_delay=0.01, backoff_factor=1.5)
    def flaky_service():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TimeoutError("Temporary network timeout")
        return "SUCCESS"

    result = flaky_service()
    assert result == "SUCCESS"
    assert attempts == 3


# ===================================================================
# 6. Synchronization Engine & Audit History
# ===================================================================
def test_sync_manager_execution_and_history(tokens):
    """Verifies manual sync execution and MongoDB audit trail generation."""
    admin_headers = {"Authorization": f"Bearer {tokens['ADMIN']}"}

    # Trigger payroll sync
    sync_res = client.post(
        "/api/v1/integrations/payroll_gateway/sync",
        json={"month": "2026-03"},
        headers=admin_headers
    )
    assert sync_res.status_code == 200
    data = sync_res.json()
    assert data["integration"] == "payroll_gateway"
    assert data["status"] == "SUCCESS"
    assert data["records_read"] == 200  # 200 employees synced

    # Query sync history
    hist_res = client.get("/api/v1/integrations/payroll_gateway/sync-history", headers=admin_headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert isinstance(history, list)
    assert len(history) > 0
    assert history[0]["integration"] == "payroll_gateway"


# ===================================================================
# 7. Webhook Security: HMAC Signature & Replay Protection
# ===================================================================
def test_webhook_security_and_idempotency():
    """Verifies HMAC-SHA256 signature verification, replay protection, and duplicate prevention."""
    secret = settings.WEBHOOK_SIGNING_SECRET
    body_data = {"event_id": f"EVT_{int(time.time())}", "action": "test_ping"}
    body_bytes = json.dumps(body_data).encode("utf-8")

    # Compute valid signature
    valid_sig = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

    # 1. Valid Signature -> 200 Accepted
    res = client.post(
        "/api/v1/integrations/webhooks/generic?event=test_event",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": valid_sig,
            "X-Webhook-Timestamp": str(time.time())
        }
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ACCEPTED"

    # 2. Tampered / Invalid Signature -> 401 Unauthorized
    bad_res = client.post(
        "/api/v1/integrations/webhooks/generic?event=test_event",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": "invalid_fake_hmac_signature_000000000000",
            "X-Webhook-Timestamp": str(time.time())
        }
    )
    assert bad_res.status_code == 401

    # 3. Expired Timestamp (Replay Attack) -> 400 Bad Request
    expired_time = str(time.time() - 1000)  # > 5 minutes ago
    replay_res = client.post(
        "/api/v1/integrations/webhooks/generic?event=test_event",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": valid_sig,
            "X-Webhook-Timestamp": expired_time
        }
    )
    assert replay_res.status_code == 400

    # 4. Duplicate Event Idempotency Check
    dup_res = client.post(
        "/api/v1/integrations/webhooks/generic?event=test_event",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": valid_sig,
            "X-Webhook-Timestamp": str(time.time())
        }
    )
    assert dup_res.status_code == 200
    assert "IDEMPOTENT_SKIP" in dup_res.json()["message"]


# ===================================================================
# 8. Biometric Punch Ingestion & Deduplication
# ===================================================================
def test_biometric_punch_ingestion():
    """Verifies biometric punch log ingestion and mapping to EMP004."""
    db = get_db()
    connector = registry.get_connector("biometric")
    assert connector is not None

    test_dev_id = f"TEST_TERM_{int(time.time())}"
    punch_payload = {
        "device_id": test_dev_id,
        "user_pin": "EMP004",
        "timestamp": "2026-10-25 08:58:30",
        "punch_type": "CheckIn"
    }

    try:
        # Initial Punch
        result1 = connector.process_punch(punch_payload)
        assert result1["status"] == "SUCCESS"
        assert result1["employee_id"] == "EMP004"

        # Duplicate Punch on same day
        result2 = connector.process_punch(punch_payload)
        assert result2["status"] == "DUPLICATE_SKIPPED"
    finally:
        db.biometric_punch_logs.delete_many({"device_id": test_dev_id})


# ===================================================================
# 9. Server-Side GPS Geofence & Anti-Spoofing Verification
# ===================================================================
def test_geofence_server_validation():
    """Verifies server-side Haversine geofence calculation and accuracy validation."""
    # InnovateCorp HQ Coordinates (e.g. Bangalore center: 12.9716, 77.5946)
    office_lat = 12.9716
    office_lon = 77.5946

    # 1. Close coordinate (~50 meters away)
    near_lat = 12.9720
    near_lon = 77.5948
    is_inside, dist, msg = GeofenceValidator.validate_attendance_location(
        client_lat=near_lat,
        client_lon=near_lon,
        target_lat=office_lat,
        target_lon=office_lon,
        allowed_radius_meters=500.0,
        accuracy_meters=15.0
    )
    assert is_inside is True
    assert dist < 100.0

    # 2. Far coordinate (5 kilometers away)
    far_lat = 13.0200
    far_lon = 77.6200
    is_inside_far, dist_far, msg_far = GeofenceValidator.validate_attendance_location(
        client_lat=far_lat,
        client_lon=far_lon,
        target_lat=office_lat,
        target_lon=office_lon,
        allowed_radius_meters=500.0,
        accuracy_meters=15.0
    )
    assert is_inside_far is False
    assert dist_far > 1000.0

    # 3. Degraded accuracy (> 250m) rejected for spoofing defense
    _, _, err_acc = GeofenceValidator.validate_attendance_location(
        client_lat=near_lat,
        client_lon=near_lon,
        target_lat=office_lat,
        target_lon=office_lon,
        accuracy_meters=350.0
    )
    assert "accuracy" in err_acc.lower()


# ===================================================================
# 10. Strict 200 Employee Database Invariant
# ===================================================================
def test_strict_200_employees_invariant():
    """In accordance with project rules, exactly 200 employees must remain."""
    db = get_db()
    total = db.employees.count_documents({})
    assert total == 200, f"Expected 200 employees, found {total}"
    assert db.employees.find_one({"employee_id": "EMP201"}) is None
