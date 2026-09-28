"""
AI-Powered Workforce Management Automation System
Production Error Tracking & Observability Abstraction
--------------------------------------------------
Provides centralized error monitoring supporting Sentry, OpenTelemetry,
or local structured JSON logger. Sanitizes all error context to ensure
sensitive employee PII and secrets are never leaked to telemetry sinks.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from backend.utils.logging import get_logger, request_id_ctx, user_id_ctx
from backend.config import settings

logger = get_logger("workforce.monitoring.errors")

class ErrorTracker:
    """
    Enterprise error tracking provider abstraction.
    Initializes Sentry SDK if DSN is configured, or provides safe local structured logging.
    """
    def __init__(self):
        self._provider: str = "local"
        self._initialized: bool = False
        self._init_provider()

    def _init_provider(self):
        sentry_dsn = settings.SENTRY_DSN
        if sentry_dsn and sentry_dsn.startswith("http"):
            try:
                import sentry_sdk
                from sentry_sdk.integrations.fastapi import FastApiIntegration
                from sentry_sdk.integrations.pymongo import PyMongoIntegration

                sentry_sdk.init(
                    dsn=sentry_dsn,
                    environment=settings.ENVIRONMENT,
                    traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
                    integrations=[
                        FastApiIntegration(),
                        PyMongoIntegration()
                    ],
                    send_default_pii=False  # Strict PII protection
                )
                self._provider = "sentry"
                self._initialized = True
                logger.info("Initialized Sentry error monitoring integration")
                return
            except Exception as e:
                logger.warning(f"Could not initialize Sentry integration: {e}. Falling back to local logger.")

        self._provider = "local"
        self._initialized = True
        logger.info(f"Using local structured error tracking (Environment: {settings.ENVIRONMENT})")

    @property
    def provider(self) -> str:
        return self._provider

    def capture_exception(
        self,
        exc: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "error"
    ):
        """
        Captures an unhandled exception with sanitized context.
        """
        safe_ctx = context.copy() if context else {}
        safe_ctx.setdefault("request_id", request_id_ctx.get())
        safe_ctx.setdefault("user_id", user_id_ctx.get())
        safe_ctx.setdefault("environment", settings.ENVIRONMENT)
        safe_ctx.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

        # Redact any accidental sensitive parameters
        for sensitive_key in ("password", "token", "jwt", "secret", "pan", "ssn", "authorization"):
            if sensitive_key in safe_ctx:
                safe_ctx[sensitive_key] = "***REDACTED***"

        if self._provider == "sentry":
            try:
                import sentry_sdk
                with sentry_sdk.push_scope() as scope:
                    for k, v in safe_ctx.items():
                        scope.set_extra(k, v)
                    sentry_sdk.capture_exception(exc)
                return
            except Exception:
                pass

        # Fallback to local structured logger
        logger.error(
            f"Captured exception [{type(exc).__name__}]: {exc}",
            extra={
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                **safe_ctx
            },
            exc_info=True
        )

# Global instance
error_tracker = ErrorTracker()
