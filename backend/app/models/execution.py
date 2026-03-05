from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import BoltResult


class Execution(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "executions"
    __table_args__ = (
        Index("ix_exec_tenant_joint_bolt_time", "tenant_id", "joint_id", "bolt_no", "timestamp"),
        Index("ix_exec_tenant_source_key", "tenant_id", "source_key", unique=True),
        Index("ix_exec_tenant_status", "tenant_id", "status"),
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    joint_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("joints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bolt_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("bolts.id", ondelete="SET NULL"), nullable=True, index=True
    )

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    bolt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_torque: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_angle: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[BoltResult] = mapped_column(Enum(BoltResult), nullable=False)

    tool_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tools.id", ondelete="SET NULL"), nullable=True, index=True
    )
    operator_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("operators.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    source_key: Mapped[str] = mapped_column(String(128), nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    joint = relationship("Joint", back_populates="executions")
    bolt = relationship("Bolt", back_populates="executions")
    tool = relationship("Tool", back_populates="executions")
    operator = relationship("Operator", back_populates="executions")
