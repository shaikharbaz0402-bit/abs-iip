from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Tool(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "tools"
    __table_args__ = (
        Index("ix_tools_tenant_tool_code", "tenant_id", "tool_code", unique=True),
        Index("ix_tools_tenant_health", "tenant_id", "health_status"),
    )

    tool_code: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    total_cycles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ok_cycles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    nok_cycles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    calibration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    health_status: Mapped[str] = mapped_column(String(32), default="Healthy", nullable=False)

    tenant = relationship("Tenant", back_populates="tools")
    executions = relationship("Execution", back_populates="tool")
    assigned_joints = relationship("Joint", back_populates="tool")


class Operator(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "operators"
    __table_args__ = (
        Index("ix_operators_tenant_name", "tenant_id", "name"),
        Index("ix_operators_tenant_code", "tenant_id", "operator_code", unique=True),
    )

    operator_code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    jobs_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_torque_deviation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    tenant = relationship("Tenant", back_populates="operators")
    executions = relationship("Execution", back_populates="operator")
