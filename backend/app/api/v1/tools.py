from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_admin, tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolOut
from app.services.audit import log_event

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("", response_model=ToolOut)
def create_tool(
    payload: ToolCreate,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_admin),
) -> ToolOut:
    tool = Tool(
        tenant_id=ctx.tenant_id,
        tool_code=payload.tool_code,
        model=payload.model,
        calibration_date=payload.calibration_date,
    )
    db.add(tool)

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="TOOL_CREATED",
        actor_user_id=ctx.user_id,
        resource_type="Tool",
        resource_id=tool.id,
        description=f"Tool {tool.tool_code} registered",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(tool)
    return ToolOut.model_validate(tool)


@router.get("", response_model=list[ToolOut])
def list_tools(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[ToolOut]:
    rows = db.scalars(select(Tool).where(Tool.tenant_id == ctx.tenant_id).order_by(Tool.tool_code.asc())).all()
    return [ToolOut.model_validate(item) for item in rows]
