"""
Authentication & Authorization FastAPI Dependencies
--------------------------------------------------
Provides dependencies for extracting current user, enforcing RBAC roles,
and validating granular permissions.
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.mongodb import get_db
from backend.auth.security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> dict:
    """
    Extracts and validates the current authenticated user from Bearer JWT token.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or invalid.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token has expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing required identification fields."
        )

    db = get_db()
    user = db.users.find_one({"user_id": user_id}, {"password_hash": 0, "_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists in system."
        )

    if not user.get("is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account. Contact HR administration."
        )

    return user

def require_role(allowed_roles: List[str]):
    """
    Dependency factory that checks if current user's role is in allowed_roles.
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "EMPLOYEE")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of the following roles: {', '.join(allowed_roles)}. Your role is '{user_role}'."
            )
        return current_user
    return role_checker

def require_self_or_roles(allowed_roles: List[str]):
    """
    Helper for endpoints where an employee can view their own data,
    or privileged roles (HR, Admin, Manager) can view the target employee's data.
    """
    def checker(target_employee_id: str, current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "EMPLOYEE")
        if user_role in allowed_roles:
            return True
        if current_user.get("employee_id") == target_employee_id:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access another employee's records."
        )
    return checker
