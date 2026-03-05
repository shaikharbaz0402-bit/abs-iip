from __future__ import annotations

from fastapi import HTTPException, status

from app.models.enums import UserRole

ROLE_WRITE = {UserRole.SUPER_ADMIN, UserRole.ABS_ENGINEER, UserRole.CLIENT_ADMIN, UserRole.CLIENT_ENGINEER}
ROLE_READ = {
    UserRole.SUPER_ADMIN,
    UserRole.ABS_ENGINEER,
    UserRole.CLIENT_ADMIN,
    UserRole.CLIENT_ENGINEER,
    UserRole.CLIENT_VIEWER,
}
ABS_ROLES = {UserRole.SUPER_ADMIN, UserRole.ABS_ENGINEER}
CLIENT_ADMIN_ROLES = {UserRole.CLIENT_ADMIN}


def require_roles(user_role: UserRole, allowed: set[UserRole]) -> None:
    if user_role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )


def is_abs_role(user_role: UserRole) -> bool:
    return user_role in ABS_ROLES
