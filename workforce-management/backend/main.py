"""
AI-Powered Workforce Management Automation System
FastAPI Backend Application Entry Point
--------------------------------------------------
Initializes application with production lifespan handlers, security headers,
correlation ID tracing, structured JSON logging, rate limiting, audit logging,
and mounts all modular REST routers with liveness/readiness health probes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.config import settings
from database.mongodb import check_connection, get_db, ensure_indexes, close_connection
from backend.utils.logging import setup_logging, get_logger
from backend.middleware.audit import AuditLogMiddleware
from backend.middleware.correlation import CorrelationIdMiddleware
from backend.middleware.security import SecurityHeadersMiddleware
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.middleware.errors import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# Initialize structured logging
setup_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
logger = get_logger("workforce.backend.main")

# Import modular routers
from backend.routers import (
    auth,
    employees,
    departments,
    attendance,
    shifts,
    leave,
    holidays,
    timesheets,
    projects,
    payroll,
    performance,
    skills,
    training,
    manager,
    hr,
    reports,
    notifications,
    ai,
    workflows,
    integrations,
    health,
    locations,
    contractors,
    compliance
)
from backend.ai.chatbot.router import router as chatbot_router
from backend.rag.indexing_service import IndexingService
from backend.events.handlers import initialize_event_handlers
from backend.workflows.scheduler import get_workflow_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan context manager for graceful startup and shutdown.
    Handles service orchestration, database index creation, and resource cleanup.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")

    # A. Initialize Event Handlers & Workflow Engine
    try:
        initialize_event_handlers()
        logger.info("Event handlers initialized")
    except Exception as e:
        logger.warning(f"Event handlers init failed: {e}")

    # B. Start Background HR Workflow Scheduler
    try:
        await get_workflow_scheduler().start()
        logger.info("Background workflow scheduler started")
    except Exception as e:
        logger.warning(f"Workflow scheduler start failed: {e}")

    # C. Guarantee RAG Policy Documents are Indexed
    try:
        IndexingService().ensure_indexed()
        logger.info("RAG policy documents index verified")
    except Exception as e:
        logger.warning(f"Could not complete automatic RAG indexing: {e}")

    # D. Ensure Database Indexes
    try:
        ensure_indexes()
        logger.info("MongoDB database indexes verified")
    except Exception as e:
        logger.warning(f"MongoDB index verification failed: {e}")

    yield

    # Clean Graceful Shutdown
    logger.info("Initiating graceful application shutdown...")
    try:
        get_workflow_scheduler().stop()
        logger.info("Workflow scheduler stopped cleanly")
    except Exception as e:
        logger.warning(f"Workflow scheduler stop failed: {e}")

    try:
        close_connection()
        logger.info("MongoDB client connections closed")
    except Exception as e:
        logger.warning(f"MongoDB connection closure failed: {e}")

    logger.info("Application shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Workforce Management Automation Platform REST API with MongoDB",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 1. Security Headers Middleware (OWASP CSP, HSTS, X-Frame-Options)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Distributed Tracing & Correlation ID Middleware (X-Request-ID, X-Correlation-ID)
app.add_middleware(CorrelationIdMiddleware)

# 3. Rate Limiting & Brute-Force Throttling Middleware
app.add_middleware(RateLimitMiddleware)

# 4. Audit Logging Middleware (Tracks mutating state in MongoDB audit_logs)
app.add_middleware(AuditLogMiddleware)

# 5. Trusted Hosts Middleware (Restricts Host header in production)
if settings.ENVIRONMENT == "production" and settings.ALLOWED_HOSTS and "*" not in settings.ALLOWED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# 6. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 7. Global Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 8. Root Endpoint
@app.get("/", tags=["System"], summary="API Root Information")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_PREFIX}/health"
    }

# 9. Register Modular Routers under /api/v1
v1_prefix = settings.API_V1_PREFIX

app.include_router(health.router, prefix=v1_prefix)
app.include_router(auth.router, prefix=v1_prefix)
app.include_router(employees.router, prefix=v1_prefix)
app.include_router(departments.router, prefix=v1_prefix)
app.include_router(attendance.router, prefix=v1_prefix)
app.include_router(shifts.router, prefix=v1_prefix)
app.include_router(leave.router, prefix=v1_prefix)
app.include_router(holidays.router, prefix=v1_prefix)
app.include_router(timesheets.router, prefix=v1_prefix)
app.include_router(projects.router, prefix=v1_prefix)
app.include_router(payroll.router, prefix=v1_prefix)
app.include_router(performance.router, prefix=v1_prefix)
app.include_router(skills.router, prefix=v1_prefix)
app.include_router(training.router, prefix=v1_prefix)
app.include_router(manager.router, prefix=v1_prefix)
app.include_router(hr.router, prefix=v1_prefix)
app.include_router(reports.router, prefix=v1_prefix)
app.include_router(notifications.router, prefix=v1_prefix)
app.include_router(workflows.router, prefix=v1_prefix)
app.include_router(ai.router, prefix=v1_prefix)
app.include_router(chatbot_router, prefix=v1_prefix)
app.include_router(integrations.router, prefix=v1_prefix)
app.include_router(locations.router, prefix=v1_prefix)
app.include_router(contractors.router, prefix=v1_prefix)
app.include_router(compliance.router, prefix=v1_prefix)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
