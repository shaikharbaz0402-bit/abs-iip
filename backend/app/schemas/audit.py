from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    event_type: str
    actor_user_id: str | None
    resource_type: str
    resource_id: str | None
    description: str
    ip_address: str | None
    created_at: datetime
