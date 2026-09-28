"""
Authentication Schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    employee_id: str
    email: str
    role: str

class UserProfileResponse(BaseModel):
    user_id: str
    employee_id: str
    email: str
    role: str
    is_active: int
    name: Optional[str] = None
    department_id: Optional[str] = None
    designation: Optional[str] = None
    created_at: Optional[str] = None
    mfa_enabled: Optional[bool] = False

class MfaStatusResponse(BaseModel):
    mfa_enabled: bool
    email: str

class MfaSetupResponse(BaseModel):
    secret: str
    otpauth_uri: str
    message: str

class MfaVerifyRequest(BaseModel):
    code: str

class MfaActionResponse(BaseModel):
    success: bool
    message: str
