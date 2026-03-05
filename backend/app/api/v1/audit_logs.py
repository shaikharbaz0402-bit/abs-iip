from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_admin
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    event_type: str | None = None,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_admin),
) -> list[AuditLogOut]:
    stmt = select(AuditLog).where(AuditLog.tenant_id == ctx.tenant_id)
    if event_type:
        stmt = stmt.where(AuditLog.event_type == event_type)

    rows = db.scalars(stmt.order_by(AuditLog.created_at.desc()).limit(1000)).all()
    return [AuditLogOut.model_validate(item) for item in rows]
