from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.billing import SubscriptionPlan, TenantSubscription
from app.models.enums import PlanType, SubscriptionStatus
from app.services.analytics import count_active_users


def get_or_create_tenant_subscription(db: Session, tenant_id: str) -> TenantSubscription:
    subscription = db.scalar(
        select(TenantSubscription).where(TenantSubscription.tenant_id == tenant_id)
    )
    if subscription is not None:
        return subscription

    plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name == PlanType.BASIC))
    if plan is None:
        raise HTTPException(status_code=500, detail="Billing plans are not initialized.")

    subscription = TenantSubscription(
        tenant_id=tenant_id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
    )
    db.add(subscription)
    db.flush()
    return subscription


def validate_seat_limit(db: Session, tenant_id: str) -> None:
    subscription = get_or_create_tenant_subscription(db, tenant_id)
    if subscription.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Subscription inactive.")

    plan = db.get(SubscriptionPlan, subscription.plan_id)
    if plan is None:
        raise HTTPException(status_code=500, detail="Plan not found.")

    used = count_active_users(db, tenant_id)
    if used >= plan.seat_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Seat limit reached for {plan.name.value} plan.",
        )


def register_usage(db: Session, tenant_id: str, amount: int = 1) -> None:
    subscription = get_or_create_tenant_subscription(db, tenant_id)
    plan = db.get(SubscriptionPlan, subscription.plan_id)
    if plan is None:
        return
    subscription.current_month_usage += amount
    if subscription.current_month_usage > plan.usage_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Monthly usage limit exceeded for current subscription plan.",
        )
