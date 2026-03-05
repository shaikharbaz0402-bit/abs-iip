from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReportType


class Report(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_tenant_project", "tenant_id", "project_id"),
        Index("ix_reports_qr_token", "qr_token", unique=True),
    )

    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType), nullable=False)
    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    work_order_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    joint_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("joints.id", ondelete="SET NULL"), nullable=True, index=True
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    qr_token: Mapped[str] = mapped_column(String(128), nullable=False)
    generated_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
