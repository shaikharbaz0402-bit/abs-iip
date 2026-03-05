from __future__ import annotations

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AIAlert(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "ai_alerts"
    __table_args__ = (
        Index("ix_ai_alerts_tenant_resolved", "tenant_id", "is_resolved"),
        Index("ix_ai_alerts_tenant_joint", "tenant_id", "joint_id"),
    )

    alert_type: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    project_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    joint_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tool_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
