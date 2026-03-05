from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin_user
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, UserCreate, UserOut
from app.services.audit import log_event
from app.services.billing import validate_seat_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> Token:

    user = db.scalar(select(User).where(User.email == payload.email, User.is_active.is_(True)))

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.last_login_at = datetime.now(timezone.utc)

    token = create_access_token(
        subject=user.id,
        tenant_id=user.tenant_id,
        role=user.role.value
    )

    log_event(
        db,
        tenant_id=user.tenant_id,
        event_type="LOGIN",
        actor_user_id=user.id,
        resource_type="User",
        resource_id=user.id,
        description=f"User {user.email} logged in",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()

    return Token(access_token=token)


@router.post("/token", response_model=Token)
def token_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:

    payload = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )

    return login(payload=payload, request=request, db=db)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)


@router.post("/users", response_model=UserOut)
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> UserOut:

    tenant_id = payload.tenant_id or current_user.tenant_id

    if current_user.role not in {UserRole.SUPER_ADMIN, UserRole.ABS_ENGINEER} and tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Cannot create users for another tenant")

    if current_user.role not in {UserRole.SUPER_ADMIN, UserRole.ABS_ENGINEER} and payload.role in {
        UserRole.SUPER_ADMIN,
        UserRole.ABS_ENGINEER,
    }:
        raise HTTPException(status_code=403, detail="Client admins cannot create ABS roles")

    validate_seat_limit(db, tenant_id)

    exists = db.scalar(select(User).where(User.email == payload.email))

    if exists is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        tenant_id=tenant_id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        is_active=True,
    )

    db.add(user)

    log_event(
        db,
        tenant_id=tenant_id,
        event_type="USER_CREATED",
        actor_user_id=current_user.id,
        resource_type="User",
        resource_id=user.id,
        description=f"User {payload.email} created with role {payload.role.value}",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(user)

    return UserOut.model_validate(user)