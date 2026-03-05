from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationMarkRead, NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[NotificationOut]:
    stmt = select(Notification).where(Notification.tenant_id == ctx.tenant_id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    rows = db.scalars(stmt.order_by(Notification.created_at.desc()).limit(500)).all()
    return [NotificationOut.model_validate(item) for item in rows]


@router.patch("/{notification_id}", response_model=NotificationOut)
def mark_notification(
    notification_id: str,
    payload: NotificationMarkRead,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> NotificationOut:
    item = db.scalar(
        select(Notification).where(Notification.id == notification_id, Notification.tenant_id == ctx.tenant_id)
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    item.is_read = payload.is_read
    db.commit()
    db.refresh(item)
    return NotificationOut.model_validate(item)
