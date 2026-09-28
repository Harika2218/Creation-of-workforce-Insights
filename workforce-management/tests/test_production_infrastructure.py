"""
AI-Powered Workforce Management Automation System
Phase 12: Production Infrastructure, Security, Monitoring & Observability Tests
--------------------------------------------------------------------------------
Comprehensive test suite validating:
- Liveness & Readiness health probes
- Structured application metrics (JSON & Prometheus)
- Distributed request correlation & tracing headers
- OWASP security headers & payload size guard
- Tiered rate limiting & brute-force throttling
- Secret provider abstraction & credential masking
- Log redaction filters
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings
from backend.security.secrets import get_secret, get_secret_manager, EnvironmentSecretProvider
from database.mongodb import mask_mongodb_uri
from backend.utils.logging import SecurityRedactionFilter
import logging

client = TestClient(app)

# -------------------------------------------------------------------
# 1. Health & Readiness Probes
# -------------------------------------------------------------------
def test_health_liveness_probe():
    """Verifies lightweight liveness probe for orchestrators."""
    res = client.get("/api/v1/health/live")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "alive"
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data

def test_health_readiness_probe_dependencies():
    """Verifies readiness probe checks database, AI models, scheduler, and integrations."""
    res = client.get("/api/v1/health/ready")
    assert res.status_code in (200, 503)
    data = res.json()
    assert data["status"] in ("healthy", "degraded", "unavailable")
    deps = data["dependencies"]
    assert "database" in deps
    assert deps["database"]["status"] == "healthy"
    assert "ai_models" in deps
    assert "workflow_scheduler" in deps
    assert "integrations" in deps
    # Integrations must report status honestly
    assert deps["integrations"]["microsoft_teams"] in ("healthy", "not_configured")

def test_legacy_health_endpoint_backward_compatibility():
    """Ensures legacy /api/v1/health endpoint remains functional."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["database"] == "connected"

# -------------------------------------------------------------------
# 2. Application Metrics (JSON & Prometheus)
# -------------------------------------------------------------------
def test_metrics_json_exposition():
    """Verifies /api/v1/metrics returns comprehensive JSON metrics snapshot."""
    res = client.get("/api/v1/metrics?format=json")
    assert res.status_code == 200
    data = res.json()
    assert "uptime_seconds" in data
    assert "http" in data
    assert "total_requests" in data["http"]
    assert "process" in data
    assert "business_events" in data
    assert "ai_workforce" in data

def test_metrics_prometheus_exposition():
    """Verifies /api/v1/metrics returns Prometheus standard exposition format."""
    res = client.get("/api/v1/metrics")
    assert res.status_code == 200
    text = res.text
    assert "# HELP hr_app_uptime_seconds" in text
    assert "# TYPE hr_http_requests_total counter" in text
    assert "hr_http_requests_total" in text

# -------------------------------------------------------------------
# 3. Request Correlation & Distributed Tracing
# -------------------------------------------------------------------
def test_correlation_id_propagation_and_generation():
    """Verifies incoming correlation IDs are echoed, or new UUIDs are generated."""
    # 1. Custom incoming request ID
    custom_id = "CORR-TEST-998877"
    res1 = client.get("/api/v1/health/live", headers={"X-Request-ID": custom_id})
    assert res1.status_code == 200
    assert res1.headers.get("X-Request-ID") == custom_id
    assert res1.headers.get("X-Correlation-ID") == custom_id
    assert "X-Response-Time-MS" in res1.headers

    # 2. Auto-generated request ID
    res2 = client.get("/api/v1/health/live")
    assert res2.status_code == 200
    gen_id = res2.headers.get("X-Request-ID")
    assert gen_id is not None
    assert gen_id.startswith("REQ_")

# -------------------------------------------------------------------
# 4. Security Headers & Payload Limits
# -------------------------------------------------------------------
def test_owasp_security_headers_present():
    """Verifies all mandatory OWASP security headers are returned."""
    res = client.get("/api/v1/health/live")
    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=(self)" in headers.get("Permissions-Policy", "")
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")

def test_oversized_payload_rejection():
    """Verifies request body length guard returns HTTP 413 for oversized payloads."""
    large_size = str(20 * 1024 * 1024) # 20 MB > 15 MB limit
    res = client.post(
        "/api/v1/attendance/check-in",
        headers={"Content-Length": large_size},
        json={"dummy": "data"}
    )
    assert res.status_code == 413
    assert "Payload Too Large" in res.json().get("error", "")

# -------------------------------------------------------------------
# 5. Tiered Rate Limiting & Throttling
# -------------------------------------------------------------------
def test_rate_limiting_tiered_enforcement():
    """Verifies that an IP hitting endpoints repeatedly receives 429 when exceeding quota."""
    test_ip = "198.51.100.77"
    # Auth limit is 10/min. Make 12 rapid requests.
    hit_429 = False
    for i in range(14):
        res = client.get(
            "/api/v1/auth/roles",
            headers={"X-Forwarded-For": test_ip, "X-Test-Rate-Limit": "enforce"}
        )
        if res.status_code == 429:
            hit_429 = True
            assert "X-RateLimit-Limit" in res.headers
            assert "Retry-After" in res.headers
            break
    assert hit_429, "Rate limiter should have triggered 429 Too Many Requests"

# -------------------------------------------------------------------
# 6. Secret Management & Credential Masking
# -------------------------------------------------------------------
def test_secret_provider_abstraction():
    """Verifies SecretProvider interface returns environment secrets without hardcoded credentials."""
    mgr = get_secret_manager()
    assert isinstance(mgr, EnvironmentSecretProvider)
    db_name = get_secret("MONGODB_DATABASE")
    assert db_name is not None
    jwt_sec = get_secret("JWT_SECRET", default=settings.JWT_SECRET)
    assert jwt_sec is not None


def test_mongodb_credential_masking():
    """Verifies connection strings with credentials are masked before logging."""
    raw_uri = "mongodb://hr_admin:SuperSecretPass123@cluster0.net:27017/hr_automation"
    masked = mask_mongodb_uri(raw_uri)
    assert "SuperSecretPass123" not in masked
    assert "***:***@" in masked

def test_security_redaction_log_filter():
    """Verifies logger redaction filter scrubs sensitive keywords and PII from log output."""
    filter_instance = SecurityRedactionFilter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="User login attempt with password=MySecretPassword123 and Authorization=Bearer eyJhbGciOiJIUzI1NiJ9",
        args=(),
        exc_info=None
    )
    filter_instance.filter(record)
    assert "MySecretPassword123" not in record.msg
    assert "***REDACTED***" in record.msg
