from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.core.deps import TenantContext, get_current_user, get_tenant_context
from app.models.enums import UserRole
from app.models.user import User


READ_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.ABS_ENGINEER,
    UserRole.CLIENT_ADMIN,
    UserRole.CLIENT_ENGINEER,
    UserRole.CLIENT_VIEWER,
}
WRITE_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.ABS_ENGINEER,
    UserRole.CLIENT_ADMIN,
    UserRole.CLIENT_ENGINEER,
}
ADMIN_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.ABS_ENGINEER,
    UserRole.CLIENT_ADMIN,
}
ABS_ROLES = {UserRole.SUPER_ADMIN, UserRole.ABS_ENGINEER}


def require_read_user(user: User = Depends(get_current_user)) -> User:
    if user.role not in READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return user


def require_write_user(user: User = Depends(get_current_user)) -> User:
    if user.role not in WRITE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Read-only user")
    return user


def require_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


def require_abs_user(user: User = Depends(get_current_user)) -> User:
    if user.role not in ABS_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ABS role required")
    return user


def tenant_context_read(
    _: User = Depends(require_read_user),
    context: TenantContext = Depends(get_tenant_context),
) -> TenantContext:
    return context


def tenant_context_write(
    _: User = Depends(require_write_user),
    context: TenantContext = Depends(get_tenant_context),
) -> TenantContext:
    return context


def tenant_context_admin(
    _: User = Depends(require_admin_user),
    context: TenantContext = Depends(get_tenant_context),
) -> TenantContext:
    return context
