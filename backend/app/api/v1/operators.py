from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_admin, tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.tool import Operator
from app.schemas.operator import OperatorCreate, OperatorOut
from app.services.audit import log_event

router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("", response_model=OperatorOut)
def create_operator(
    payload: OperatorCreate,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_admin),
) -> OperatorOut:
    operator = Operator(
        tenant_id=ctx.tenant_id,
        operator_code=payload.operator_code,
        name=payload.name,
    )
    db.add(operator)

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="OPERATOR_CREATED",
        actor_user_id=ctx.user_id,
        resource_type="Operator",
        resource_id=operator.id,
        description=f"Operator {operator.operator_code} registered",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(operator)
    return OperatorOut.model_validate(operator)


@router.get("", response_model=list[OperatorOut])
def list_operators(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[OperatorOut]:
    rows = db.scalars(
        select(Operator).where(Operator.tenant_id == ctx.tenant_id).order_by(Operator.name.asc())
    ).all()
    return [OperatorOut.model_validate(item) for item in rows]
