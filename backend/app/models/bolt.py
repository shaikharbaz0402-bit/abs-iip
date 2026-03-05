from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import BoltResult


class Bolt(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "bolts"
    __table_args__ = (
        Index("ix_bolts_tenant_joint_bolt", "tenant_id", "joint_id", "bolt_no", unique=True),
        Index("ix_bolts_tenant_result", "tenant_id", "result"),
    )

    joint_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("joints.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bolt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    target_torque: Mapped[float] = mapped_column(Float, nullable=False)
    target_angle: Mapped[float | None] = mapped_column(Float, nullable=True)
    result: Mapped[BoltResult] = mapped_column(
        Enum(BoltResult), default=BoltResult.MISSING, nullable=False
    )

    joint = relationship("Joint", back_populates="bolts")
    executions = relationship("Execution", back_populates="bolt", cascade="all, delete-orphan")
