from __future__ import annotations

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Branding(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "branding"
    __table_args__ = (Index("ix_branding_tenant", "tenant_id", unique=True),)

    company_logo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(16), default="#0f4c81", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(16), default="#1f2937", nullable=False)
    client_display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    tenant = relationship("Tenant", back_populates="branding")
