"""
Authentication Router
---------------------
Handles user login and current session identification.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from database.mongodb import get_db
from backend.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserProfileResponse,
    MfaStatusResponse,
    MfaSetupResponse,
    MfaVerifyRequest,
    MfaActionResponse
)
from backend.auth.security import (
    verify_password,
    create_access_token,
    generate_totp_secret,
    verify_totp_code
)
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse, summary="Authenticate user and obtain JWT token")
async def login(credentials: LoginRequest):
    """
    Authenticates an employee, manager, HR, or admin using email and password.
    Supports optional RFC 6238 TOTP multi-factor authentication.
    Returns a signed JWT bearer token.
    """
    db = get_db()
    user = db.users.find_one({"email": credentials.email.lower()})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not verify_password(credentials.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.get("is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently inactive. Contact HR."
        )

    # Multi-Factor Authentication enforcement
    if user.get("mfa_enabled", False):
        if not credentials.mfa_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA_REQUIRED: Multi-Factor Authentication code required."
            )
        secret = user.get("mfa_secret", "")
        if not verify_totp_code(secret, credentials.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA verification code."
            )

    token = create_access_token({
        "sub": user["user_id"],
        "employee_id": user["employee_id"],
        "email": user["email"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["user_id"],
        "employee_id": user["employee_id"],
        "email": user["email"],
        "role": user["role"]
    }

@router.get("/me", response_model=UserProfileResponse, summary="Get current logged in user profile")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Returns the authenticated user's account details.
    """
    db = get_db()
    emp = db.employees.find_one({"employee_id": current_user["employee_id"]}, {"name": 1, "department_id": 1, "designation": 1})
    res = dict(current_user)
    if emp:
        res["name"] = emp.get("name")
        res["department_id"] = emp.get("department_id")
        res["designation"] = emp.get("designation")
    else:
        res["name"] = current_user["email"].split("@")[0].title()
    res["mfa_enabled"] = bool(current_user.get("mfa_enabled", False))
    return res

# -------------------------------------------------------------------
# Multi-Factor Authentication (MFA) Management
# -------------------------------------------------------------------
@router.get("/mfa/status", response_model=MfaStatusResponse, summary="Get MFA status for current user")
async def get_mfa_status(current_user: dict = Depends(get_current_user)):
    return {
        "mfa_enabled": bool(current_user.get("mfa_enabled", False)),
        "email": current_user["email"]
    }

@router.post("/mfa/setup", response_model=MfaSetupResponse, summary="Generate new TOTP secret for authenticator setup")
async def setup_mfa(current_user: dict = Depends(get_current_user)):
    db = get_db()
    secret = generate_totp_secret()
    db.users.update_one(
        {"user_id": current_user["user_id"]},
        {"$set": {"pending_mfa_secret": secret}}
    )
    issuer = "InnovateCorp-HR"
    account = current_user["email"]
    otpauth = f"otpauth://totp/{issuer}:{account}?secret={secret}&issuer={issuer}"
    return {
        "secret": secret,
        "otpauth_uri": otpauth,
        "message": "Scan the QR code or enter this secret into your authenticator app, then verify with /auth/mfa/enable."
    }

@router.post("/mfa/enable", response_model=MfaActionResponse, summary="Verify TOTP code and enable MFA")
async def enable_mfa(body: MfaVerifyRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = db.users.find_one({"user_id": current_user["user_id"]})
    secret = user.get("pending_mfa_secret") or user.get("mfa_secret")
    if not secret:
        raise HTTPException(status_code=400, detail="MFA setup has not been initiated. Call /auth/mfa/setup first.")

    if not verify_totp_code(secret, body.code):
        raise HTTPException(status_code=400, detail="Invalid verification code. Please check your authenticator clock.")

    db.users.update_one(
        {"user_id": current_user["user_id"]},
        {
            "$set": {"mfa_enabled": True, "mfa_secret": secret},
            "$unset": {"pending_mfa_secret": ""}
        }
    )
    return {"success": True, "message": "Multi-factor authentication enabled successfully."}

@router.post("/mfa/disable", response_model=MfaActionResponse, summary="Disable MFA with verification code")
async def disable_mfa(body: MfaVerifyRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = db.users.find_one({"user_id": current_user["user_id"]})
    if not user.get("mfa_enabled"):
        return {"success": True, "message": "MFA is not enabled."}

    secret = user.get("mfa_secret", "")
    if not verify_totp_code(secret, body.code):
        raise HTTPException(status_code=400, detail="Invalid verification code.")

    db.users.update_one(
        {"user_id": current_user["user_id"]},
        {"$set": {"mfa_enabled": False}, "$unset": {"mfa_secret": "", "pending_mfa_secret": ""}}
    )
    return {"success": True, "message": "Multi-factor authentication disabled successfully."}
