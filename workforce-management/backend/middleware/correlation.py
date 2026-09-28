"""
AI-Powered Workforce Management Automation System
Request Correlation & Distributed Tracing Middleware
--------------------------------------------------
Extracts or generates an immutable X-Request-ID and X-Correlation-ID for every
HTTP transaction. Injects the ID into async context vars for structured logging,
and returns it on all outgoing HTTP response headers.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from backend.utils.logging import request_id_ctx, user_id_ctx, get_logger
from backend.auth.security import decode_access_token

logger = get_logger("workforce.http.access")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Extract or generate Request ID / Correlation ID
        incoming_id = request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID")
        request_id = incoming_id if incoming_id else f"REQ_{uuid.uuid4().hex[:12].upper()}"

        # 2. Extract User ID from Authorization header if present
        user_id = "ANONYMOUS"
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                if payload and "sub" in payload:
                    user_id = payload["sub"]
            except Exception:
                pass

        # 3. Bind context variables for this coroutine execution
        token_req = request_id_ctx.set(request_id)
        token_usr = user_id_ctx.set(user_id)

        # Attach request_id to request state for access in endpoint handlers
        request.state.request_id = request_id
        request.state.user_id = user_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # 4. Attach correlation headers to the response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = request_id
            response.headers["X-Response-Time-MS"] = str(duration_ms)

            # 5. Record request metrics
            from backend.monitoring.metrics import metrics
            metrics.record_request(request.method, request.url.path, response.status_code, duration_ms)

            # Avoid spamming access logs on health check endpoints unless error
            if "/health" not in request.url.path or response.status_code >= 400:
                logger.info(
                    f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                    extra={
                        "endpoint": request.url.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms
                    }
                )

            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            from backend.monitoring.metrics import metrics
            from backend.monitoring.error_tracker import error_tracker
            metrics.record_request(request.method, request.url.path, 500, duration_ms)
            error_tracker.capture_exception(exc, {"endpoint": request.url.path, "method": request.method})

            logger.error(
                f"{request.method} {request.url.path} FAILED after {duration_ms}ms: {exc}",
                extra={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "duration_ms": duration_ms,
                    "error": str(exc)
                },
                exc_info=True
            )
            raise
        finally:
            # Reset context variables
            request_id_ctx.reset(token_req)
            user_id_ctx.reset(token_usr)

