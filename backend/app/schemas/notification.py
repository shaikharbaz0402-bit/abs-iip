from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationSeverity, NotificationType


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    notification_type: NotificationType
    severity: NotificationSeverity
    title: str
    message: str
    is_read: bool
    project_id: str | None
    joint_id: str | None
    tool_id: str | None


class NotificationMarkRead(BaseModel):
    is_read: bool = True
