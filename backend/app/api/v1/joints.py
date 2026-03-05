from __future__ import annotations

import math

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read, tenant_context_write
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.bolt import Bolt
from app.models.enums import BoltResult
from app.models.joint import Joint
from app.schemas.joint import JointOut, JointVINAssign
from app.services.audit import log_event

router = APIRouter(prefix="/joints", tags=["joints"])


@router.get("", response_model=list[JointOut])
def list_joints(
    project_id: str | None = None,
    work_order_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[JointOut]:
    stmt = select(Joint).where(Joint.tenant_id == ctx.tenant_id)
    if project_id:
        stmt = stmt.where(Joint.project_id == project_id)
    if work_order_id:
        stmt = stmt.where(Joint.work_order_id == work_order_id)

    rows = db.scalars(stmt.order_by(Joint.joint_id.asc())).all()
    return [JointOut.model_validate(item) for item in rows]


@router.get("/{joint_uuid}", response_model=JointOut)
def get_joint(
    joint_uuid: str,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> JointOut:
    joint = db.scalar(select(Joint).where(Joint.id == joint_uuid, Joint.tenant_id == ctx.tenant_id))
    if joint is None:
        raise HTTPException(status_code=404, detail="Joint not found")
    return JointOut.model_validate(joint)


@router.patch("/{joint_uuid}/assign-vin", response_model=JointOut)
def assign_joint_vin(
    joint_uuid: str,
    payload: JointVINAssign,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_write),
) -> JointOut:
    joint = db.scalar(select(Joint).where(Joint.id == joint_uuid, Joint.tenant_id == ctx.tenant_id))
    if joint is None:
        raise HTTPException(status_code=404, detail="Joint not found")

    duplicate = db.scalar(
        select(Joint).where(
            Joint.tenant_id == ctx.tenant_id,
            Joint.assigned_vin == payload.assigned_vin,
            Joint.id != joint.id,
        )
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="VIN already assigned to another joint")

    joint.assigned_vin = payload.assigned_vin
    joint.assigned_tool_id = payload.assigned_tool_id

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="JOINT_VIN_ASSIGNED",
        actor_user_id=ctx.user_id,
        resource_type="Joint",
        resource_id=joint.id,
        description=f"VIN {payload.assigned_vin} assigned to joint {joint.joint_id}",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(joint)
    return JointOut.model_validate(joint)


@router.get("/{joint_uuid}/layout")
def get_joint_layout(
    joint_uuid: str,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> dict:
    joint = db.scalar(select(Joint).where(Joint.id == joint_uuid, Joint.tenant_id == ctx.tenant_id))
    if joint is None:
        raise HTTPException(status_code=404, detail="Joint not found")

    bolts = db.scalars(select(Bolt).where(Bolt.tenant_id == ctx.tenant_id, Bolt.joint_id == joint.id)).all()
    by_no = {bolt.bolt_no: bolt for bolt in bolts}

    nodes = []
    radius = 120
    center_x = 150
    center_y = 150

    for bolt_no in range(1, joint.bolt_count + 1):
        theta = (2 * math.pi * (bolt_no - 1)) / max(joint.bolt_count, 1)
        x = center_x + radius * math.cos(theta)
        y = center_y + radius * math.sin(theta)

        result = by_no.get(bolt_no).result if bolt_no in by_no else BoltResult.MISSING
        if result == BoltResult.OK:
            color = "#16a34a"
        elif result == BoltResult.NOK:
            color = "#dc2626"
        elif result == BoltResult.OUT_OF_TOLERANCE:
            color = "#f59e0b"
        else:
            color = "#9ca3af"

        nodes.append(
            {
                "bolt_no": bolt_no,
                "x": round(x, 2),
                "y": round(y, 2),
                "color": color,
                "status": result.value,
            }
        )

    return {
        "joint_id": joint.joint_id,
        "bolt_count": joint.bolt_count,
        "nodes": nodes,
    }
