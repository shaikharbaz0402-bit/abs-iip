from __future__ import annotations

from sqlalchemy import Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import NotificationSeverity, NotificationType


class Notification(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_tenant_unread", "tenant_id", "is_read"),
        Index("ix_notifications_tenant_type", "tenant_id", "notification_type"),
    )

    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    severity: Mapped[NotificationSeverity] = mapped_column(
        Enum(NotificationSeverity), default=NotificationSeverity.INFO, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    project_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    joint_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tool_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
