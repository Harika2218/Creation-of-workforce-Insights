"""
AI-Powered Workforce Management Automation System
Security Headers & Request Guard Middleware
--------------------------------------------------
Enforces OWASP-recommended security headers (CSP, HSTS, X-Content-Type-Options,
X-Frame-Options, Referrer-Policy, Permissions-Policy) and safeguards against
denial-of-service via oversized request payloads.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from backend.config import settings

# 15 MB maximum payload size (allows HR document / avatar uploads while guarding against memory exhaustion)
MAX_REQUEST_BODY_BYTES = 15 * 1024 * 1024

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Payload size guard
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length_int = int(content_length)
                if length_int > MAX_REQUEST_BODY_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Payload Too Large",
                            "detail": f"Request body exceeds the maximum permitted limit of {MAX_REQUEST_BODY_BYTES // (1024*1024)} MB.",
                            "status_code": 413,
                            "path": request.url.path
                        }
                    )
            except ValueError:
                pass

        # 2. Proceed with request processing
        response: Response = await call_next(request)

        # 3. Inject hardened security response headers
        headers = response.headers

        # Prevent MIME type sniffing
        headers["X-Content-Type-Options"] = "nosniff"

        # Frame protection against clickjacking
        headers["X-Frame-Options"] = "DENY"

        # Referrer Policy
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy: allow geolocation & camera for attendance, deny unnecessary features
        headers["Permissions-Policy"] = "geolocation=(self), camera=(self), microphone=(), payment=(), usb=()"

        # Cross-Site Scripting (XSS) Protection legacy header
        headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy (tuned for React, Vite, PWA, Three.js WebGL, Google Fonts, and WebSockets)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob: https:; "
            "connect-src 'self' ws: wss: http: https:; "
            "media-src 'self' blob:; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        headers["Content-Security-Policy"] = csp

        # Strict-Transport-Security (HSTS)
        # Apply in production or when connection is verified as HTTPS
        is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
        if is_https or settings.ENVIRONMENT == "production":
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response
