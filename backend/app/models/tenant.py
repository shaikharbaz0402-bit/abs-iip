from __future__ import annotations

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tenants"
    __table_args__ = (Index("ix_tenants_slug", "slug", unique=True),)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan")
    sites = relationship("Site", back_populates="tenant", cascade="all, delete-orphan")
    tools = relationship("Tool", back_populates="tenant", cascade="all, delete-orphan")
    operators = relationship("Operator", back_populates="tenant", cascade="all, delete-orphan")
    branding = relationship("Branding", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    subscription = relationship(
        "TenantSubscription", back_populates="tenant", uselist=False, cascade="all, delete-orphan"
    )
