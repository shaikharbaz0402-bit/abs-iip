from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PlanType, SubscriptionStatus


class SubscriptionPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscription_plans"
    __table_args__ = (Index("ix_subscription_plans_name", "name", unique=True),)

    name: Mapped[PlanType] = mapped_column(Enum(PlanType), nullable=False)
    monthly_price: Mapped[float] = mapped_column(Float, nullable=False)
    seat_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    usage_limit: Mapped[int] = mapped_column(Integer, nullable=False)


class TenantSubscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tenant_subscriptions"
    __table_args__ = (Index("ix_tenant_subscriptions_tenant", "tenant_id", unique=True),)

    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subscription_plans.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False
    )
    seats_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_month_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    tenant = relationship("Tenant", back_populates="subscription")
    plan = relationship("SubscriptionPlan")
