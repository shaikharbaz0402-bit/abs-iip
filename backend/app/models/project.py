from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Site(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "sites"
    __table_args__ = (Index("ix_sites_tenant_name", "tenant_id", "name"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    projects = relationship("Project", back_populates="site")
    tenant = relationship("Tenant", back_populates="sites")


class Project(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "projects"
    __table_args__ = (Index("ix_projects_tenant_name", "tenant_id", "name"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_completion: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="Active", nullable=False)

    site_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True
    )

    tenant = relationship("Tenant", back_populates="projects")
    site = relationship("Site", back_populates="projects")
    work_orders = relationship("WorkOrder", back_populates="project", cascade="all, delete-orphan")
    joints = relationship("Joint", back_populates="project", cascade="all, delete-orphan")
