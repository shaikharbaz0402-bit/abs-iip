from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import JointStatus


class Joint(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "joints"
    __table_args__ = (
        Index("ix_joints_tenant_workorder", "tenant_id", "work_order_id"),
        Index("ix_joints_tenant_joint_id", "tenant_id", "joint_id", unique=True),
        Index("ix_joints_tenant_status", "tenant_id", "status"),
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    work_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )

    joint_id: Mapped[str] = mapped_column(String(128), nullable=False)
    bolt_count: Mapped[int] = mapped_column(Integer, nullable=False)
    target_torque: Mapped[float] = mapped_column(Float, nullable=False)
    torque_tolerance: Mapped[float] = mapped_column(Float, nullable=False)
    angle_tolerance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[JointStatus] = mapped_column(
        Enum(JointStatus), default=JointStatus.PENDING, nullable=False
    )

    assigned_vin: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    assigned_tool_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tools.id", ondelete="SET NULL"), nullable=True, index=True
    )

    project = relationship("Project", back_populates="joints")
    work_order = relationship("WorkOrder", back_populates="joints")
    bolts = relationship("Bolt", back_populates="joint", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="joint", cascade="all, delete-orphan")
    tool = relationship("Tool", back_populates="assigned_joints")
