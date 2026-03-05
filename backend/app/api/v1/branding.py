from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_admin, tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.branding import Branding
from app.schemas.branding import BrandingOut, BrandingUpdate
from app.services.audit import log_event

router = APIRouter(prefix="/branding", tags=["branding"])


@router.get("", response_model=BrandingOut | None)
def get_branding(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
):
    item = db.scalar(select(Branding).where(Branding.tenant_id == ctx.tenant_id))
    return BrandingOut.model_validate(item) if item else None


@router.put("", response_model=BrandingOut)
def upsert_branding(
    payload: BrandingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_admin),
) -> BrandingOut:
    item = db.scalar(select(Branding).where(Branding.tenant_id == ctx.tenant_id))
    if item is None:
        item = Branding(
            tenant_id=ctx.tenant_id,
            client_display_name=payload.client_display_name,
            primary_color=payload.primary_color,
            secondary_color=payload.secondary_color,
            company_logo_path=payload.company_logo_path,
        )
        db.add(item)
    else:
        item.client_display_name = payload.client_display_name
        item.primary_color = payload.primary_color
        item.secondary_color = payload.secondary_color
        item.company_logo_path = payload.company_logo_path

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="BRANDING_UPDATED",
        actor_user_id=ctx.user_id,
        resource_type="Branding",
        resource_id=item.id,
        description="Tenant branding updated",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(item)
    return BrandingOut.model_validate(item)
