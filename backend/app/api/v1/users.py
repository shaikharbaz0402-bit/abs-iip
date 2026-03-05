from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_admin
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_admin),
) -> list[UserOut]:
    rows = db.scalars(select(User).where(User.tenant_id == ctx.tenant_id).order_by(User.email.asc())).all()
    return [UserOut.model_validate(item) for item in rows]
