from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_event(
    db: Session,
    *,
    tenant_id: str,
    event_type: str,
    actor_user_id: str | None,
    resource_type: str,
    resource_id: str | None,
    description: str,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        tenant_id=tenant_id,
        event_type=event_type,
        actor_user_id=actor_user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=ip_address,
    )
    db.add(entry)
    return entry
