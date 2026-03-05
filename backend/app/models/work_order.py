from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WorkOrder(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "work_orders"
    __table_args__ = (
        Index("ix_work_orders_tenant_project", "tenant_id", "project_id"),
        Index("ix_work_orders_tenant_code", "tenant_id", "code", unique=True),
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    uploaded_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    project = relationship("Project", back_populates="work_orders")
    joints = relationship("Joint", back_populates="work_order", cascade="all, delete-orphan")
