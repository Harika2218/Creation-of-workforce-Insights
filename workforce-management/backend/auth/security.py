"""
Authentication & Security Functions
-----------------------------------
Password hashing and JWT token encoding/decoding.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import jwt
from backend.config import settings

def hash_password(password: str) -> str:
    """Hashes password with SHA-256 matching Phase 1/2 demo seed."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against hashed password."""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# ===================================================================
# Multi-Factor Authentication (RFC 6238 TOTP Standard)
# ===================================================================
import hmac
import time
import struct
import base64
import secrets

def generate_totp_secret() -> str:
    """Generates a secure Base32-encoded 160-bit TOTP secret key."""
    random_bytes = secrets.token_bytes(20)
    return base64.b32encode(random_bytes).decode("utf-8").replace("=", "")

def get_totp_code(secret: str, time_step: Optional[int] = None) -> str:
    """
    Computes standard 6-digit TOTP code for the given secret at time_step (or now).
    Follows RFC 6238 and RFC 4226 HMAC-SHA1 specification with 30-second steps.
    """
    # Pad secret if padding was stripped
    padded_secret = secret + "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(padded_secret, casefold=True)
    if time_step is None:
        time_step = int(time.time() // 30)

    msg = struct.pack(">Q", time_step)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1000000
    return f"{code:06d}"

def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """
    Validates a 6-digit TOTP code against the secret, allowing +/- window steps (default +/- 30s)
    to accommodate reasonable device clock drift.
    """
    if not secret or not code or len(code.strip()) != 6:
        return False
    current_step = int(time.time() // 30)
    clean_code = code.strip()
    for step_offset in range(-window, window + 1):
        if get_totp_code(secret, current_step + step_offset) == clean_code:
            return True
    return False
