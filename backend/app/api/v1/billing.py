from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_abs_user, tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.billing import SubscriptionPlan, TenantSubscription
from app.models.enums import SubscriptionStatus
from app.models.user import User
from app.schemas.billing import PlanOut, SubscriptionOut, SubscriptionUpdate
from app.services.audit import log_event
from app.services.billing import get_or_create_tenant_subscription

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db), _: TenantContext = Depends(tenant_context_read)):
    rows = db.scalars(select(SubscriptionPlan).order_by(SubscriptionPlan.monthly_price.asc())).all()
    return [PlanOut.model_validate(item) for item in rows]


@router.get("/subscription", response_model=SubscriptionOut)
def current_subscription(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
):
    sub = get_or_create_tenant_subscription(db, ctx.tenant_id)
    db.commit()
    db.refresh(sub)
    return SubscriptionOut.model_validate(sub)


@router.put("/subscription", response_model=SubscriptionOut)
def update_subscription(
    payload: SubscriptionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_abs_user),
):
    plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name == payload.plan_name))
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    sub = db.scalar(select(TenantSubscription).where(TenantSubscription.tenant_id == payload.tenant_id))
    if sub is None:
        sub = TenantSubscription(tenant_id=payload.tenant_id, plan_id=plan.id, status=payload.status)
        db.add(sub)
    else:
        sub.plan_id = plan.id
        sub.status = payload.status
        if payload.status == SubscriptionStatus.CANCELLED:
            sub.current_month_usage = 0

    log_event(
        db,
        tenant_id=payload.tenant_id,
        event_type="SUBSCRIPTION_UPDATED",
        actor_user_id=user.id,
        resource_type="TenantSubscription",
        resource_id=sub.id,
        description=f"Subscription set to {payload.plan_name.value} ({payload.status.value})",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(sub)
    return SubscriptionOut.model_validate(sub)
