"""
Audit Logging Middleware
------------------------
Logs modifying HTTP actions (POST, PUT, PATCH, DELETE) to the MongoDB audit_logs collection.
"""

from datetime import datetime, timezone
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from database.mongodb import get_db
from backend.auth.security import decode_access_token

class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only log mutating actions or authentication attempts
        if request.method in ["POST", "PUT", "PATCH", "DELETE"] or "/auth/login" in request.url.path:
            try:
                # Extract user if Authorization header present
                user_id = "ANONYMOUS"
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    payload = decode_access_token(token)
                    if payload and "sub" in payload:
                        user_id = payload["sub"]

                client_ip = request.client.host if request.client else "unknown"
                db = get_db()
                audit_record = {
                    "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "user_id": user_id,
                    "action": f"{request.method} {request.url.path}",
                    "status_code": response.status_code,
                    "ip_address": client_ip,
                    "query_params": str(request.query_params)
                }
                db.audit_logs.insert_one(audit_record)
            except Exception as e:
                # Silently catch to avoid breaking the user request
                print(f"[WARN] Audit log recording failed: {e}")

        return response
