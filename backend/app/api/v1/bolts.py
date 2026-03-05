from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.bolt import Bolt
from app.schemas.bolt import BoltOut

router = APIRouter(prefix="/bolts", tags=["bolts"])


@router.get("", response_model=list[BoltOut])
def list_bolts(
    joint_id: str,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[BoltOut]:
    rows = db.scalars(
        select(Bolt)
        .where(Bolt.tenant_id == ctx.tenant_id, Bolt.joint_id == joint_id)
        .order_by(Bolt.bolt_no.asc())
    ).all()
    return [BoltOut.model_validate(item) for item in rows]
