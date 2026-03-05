from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_abs_user
from app.db.session import get_db
from app.models.billing import SubscriptionPlan, TenantSubscription
from app.models.enums import PlanType, SubscriptionStatus
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantOut
from app.services.audit import log_event

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=list[TenantOut])
def list_tenants(
    db: Session = Depends(get_db),
    _: User = Depends(require_abs_user),
) -> list[TenantOut]:
    items = db.scalars(select(Tenant).order_by(Tenant.name.asc())).all()
    return [TenantOut.model_validate(item) for item in items]


@router.post("", response_model=TenantOut)
def create_tenant(
    payload: TenantCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_abs_user),
) -> TenantOut:
    exists = db.scalar(select(Tenant).where(Tenant.slug == payload.slug))
    if exists is not None:
        raise HTTPException(status_code=409, detail="Tenant slug already exists")

    tenant = Tenant(name=payload.name, slug=payload.slug, contact_email=payload.contact_email)
    db.add(tenant)
    db.flush()

    plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name == PlanType.BASIC))
    if plan is not None:
        db.add(
            TenantSubscription(
                tenant_id=tenant.id,
                plan_id=plan.id,
                status=SubscriptionStatus.ACTIVE,
            )
        )

    log_event(
        db,
        tenant_id=tenant.id,
        event_type="TENANT_CREATED",
        actor_user_id=user.id,
        resource_type="Tenant",
        resource_id=tenant.id,
        description=f"Tenant {tenant.name} created",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(tenant)
    return TenantOut.model_validate(tenant)
