"""
AI-Powered Workforce Management Automation System
Production Rate Limiting & Brute-Force Throttling
--------------------------------------------------
Implements tiered in-memory sliding-window rate limiting and brute-force
login protection. Emits RFC-standard rate limit response headers:
- X-RateLimit-Limit
- X-RateLimit-Remaining
- X-RateLimit-Reset
- Retry-After
"""

import time
from typing import Dict, Tuple, List
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from backend.config import settings
from backend.utils.logging import get_logger

logger = get_logger("workforce.security.rate_limit")

class RateLimiter:
    """
    In-memory sliding-window rate limiter per client IP / identifier.
    Cleanly decoupled for drop-in Redis cluster backend in distributed cloud setups.
    """
    def __init__(self):
        # Maps key -> list of request timestamps
        self._requests: Dict[str, List[float]] = defaultdict(list)
        # Maps IP -> list of failed login timestamps for brute force throttling
        self._failed_logins: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        """
        Evaluates whether key has exceeded max_requests in window_seconds.
        Returns: (is_limited, remaining_quota, reset_time_seconds)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Prune older entries
        recent = [ts for ts in self._requests[key] if ts > window_start]
        self._requests[key] = recent

        remaining = max(0, max_requests - len(recent))
        reset_time = int(window_seconds - (now - recent[0])) if recent else window_seconds

        if len(recent) >= max_requests:
            return True, 0, reset_time

        # Record this request
        self._requests[key].append(now)
        return False, remaining - 1, reset_time

    def record_failed_login(self, client_ip: str):
        """Records a failed login attempt for brute force tracking."""
        now = time.time()
        self._failed_logins[client_ip].append(now)

    def clear_failed_logins(self, client_ip: str):
        """Clears failed login count upon successful authentication."""
        if client_ip in self._failed_logins:
            del self._failed_logins[client_ip]

    def is_brute_force_throttled(self, client_ip: str, max_failures: int = 5, lock_seconds: int = 300) -> Tuple[bool, int]:
        """
        Checks if client_ip has exceeded max_failures within lock_seconds window.
        Returns: (is_throttled, seconds_remaining)
        """
        now = time.time()
        window_start = now - lock_seconds
        recent = [ts for ts in self._failed_logins[client_ip] if ts > window_start]
        self._failed_logins[client_ip] = recent

        if len(recent) >= max_failures:
            earliest_failure = recent[0]
            remaining_lock = int(lock_seconds - (now - earliest_failure))
            return True, max(1, remaining_lock)
        return False, 0

# Global limiter instance
limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Bypass in test environment or if globally disabled
        if not settings.RATE_LIMIT_ENABLED or settings.ENVIRONMENT == "test":
            return await call_next(request)

        # Bypass static files, docs, and health checks
        path = request.url.path
        if path in ("/docs", "/redoc", "/openapi.json") or path.startswith(f"{settings.API_V1_PREFIX}/health"):
            return await call_next(request)

        # Extract client IP with X-Forwarded-For support
        client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()

        # In non-production environments, bypass TestClient unless explicitly testing rate limits
        if client_ip == "testclient" and settings.ENVIRONMENT != "production" and not request.headers.get("X-Test-Rate-Limit"):
            return await call_next(request)

        # 1. Brute force check on login endpoint
        if path.endswith("/auth/login") and request.method == "POST":
            is_throttled, lock_remaining = limiter.is_brute_force_throttled(client_ip, max_failures=8, lock_seconds=300)
            if is_throttled:
                logger.warning(
                    f"Brute force protection triggered for IP {client_ip}. Throttled for {lock_remaining}s.",
                    extra={"client_ip": client_ip, "lock_remaining": lock_remaining}
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "detail": f"Too many failed login attempts. Temporary cooldown in effect. Try again in {lock_remaining} seconds.",
                        "status_code": 429,
                        "retry_after_seconds": lock_remaining
                    },
                    headers={"Retry-After": str(lock_remaining)}
                )

        # 2. Determine tiered limit by endpoint category
        if "/auth/" in path:
            max_limit = settings.RATE_LIMIT_AUTH_PER_MINUTE
            category = "auth"
        elif "/ai/" in path or "/chatbot/" in path:
            max_limit = settings.RATE_LIMIT_AI_PER_MINUTE
            category = "ai"
        elif "/integrations/webhooks/" in path:
            max_limit = 60
            category = "webhooks"
        else:
            max_limit = settings.RATE_LIMIT_GENERAL_PER_MINUTE
            category = "general"

        rate_key = f"{client_ip}:{category}"
        is_limited, remaining, reset_secs = limiter.is_rate_limited(rate_key, max_limit, window_seconds=60)

        if is_limited:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on category '{category}'. Limit: {max_limit}/min.",
                extra={"client_ip": client_ip, "category": category, "reset_secs": reset_secs}
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": f"Rate limit of {max_limit} requests/minute for category '{category}' exceeded. Retry in {reset_secs} seconds.",
                    "status_code": 429,
                    "retry_after_seconds": reset_secs
                },
                headers={
                    "Retry-After": str(reset_secs),
                    "X-RateLimit-Limit": str(max_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_secs)
                }
            )

        response = await call_next(request)

        # Attach rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(max_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_secs)

        # Check for authentication failures to feed brute force tracking
        if path.endswith("/auth/login") and request.method == "POST":
            if response.status_code == 401:
                limiter.record_failed_login(client_ip)
            elif response.status_code == 200:
                limiter.clear_failed_logins(client_ip)

        return response
