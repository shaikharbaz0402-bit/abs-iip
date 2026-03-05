from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read, tenant_context_write
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.bolt import Bolt
from app.models.enums import BoltResult, JointStatus
from app.models.joint import Joint
from app.models.project import Project
from app.models.work_order import WorkOrder
from app.schemas.work_order import WorkOrderOut, WorkOrderUploadResult
from app.services.audit import log_event
from app.services.parser import parse_work_order_excel, sha256_bytes

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


@router.get("", response_model=list[WorkOrderOut])
def list_work_orders(
    project_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[WorkOrderOut]:
    stmt = select(WorkOrder).where(WorkOrder.tenant_id == ctx.tenant_id)
    if project_id:
        stmt = stmt.where(WorkOrder.project_id == project_id)

    rows = db.scalars(stmt.order_by(WorkOrder.created_at.desc())).all()
    return [WorkOrderOut.model_validate(item) for item in rows]


@router.post("/upload", response_model=WorkOrderUploadResult)
async def upload_work_order(
    request: Request,
    project_id: str = Form(...),
    code: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_write),
) -> WorkOrderUploadResult:
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.tenant_id == ctx.tenant_id)
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found for tenant")

    file_bytes = await file.read()
    source_hash = sha256_bytes(file_bytes)

    existing = db.scalar(
        select(WorkOrder).where(
            WorkOrder.tenant_id == ctx.tenant_id,
            WorkOrder.source_hash == source_hash,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Work order file already uploaded")

    records = parse_work_order_excel(file_bytes)

    work_order = WorkOrder(
        tenant_id=ctx.tenant_id,
        project_id=project_id,
        code=code,
        name=name,
        source_filename=file.filename or "work_order.xlsx",
        source_hash=source_hash,
        uploaded_by_user_id=ctx.user_id,
    )
    db.add(work_order)
    db.flush()

    joints_created = 0
    bolts_created = 0

    for record in records:
        joint = Joint(
            tenant_id=ctx.tenant_id,
            project_id=project_id,
            work_order_id=work_order.id,
            joint_id=record["joint_id"],
            bolt_count=record["bolt_count"],
            target_torque=record["target_torque"],
            torque_tolerance=record["torque_tolerance"],
            angle_tolerance=record["angle_tolerance"],
            assigned_vin=record.get("assigned_vin"),
            status=JointStatus.PENDING,
        )
        db.add(joint)
        db.flush()
        joints_created += 1

        for bolt_no in range(1, record["bolt_count"] + 1):
            db.add(
                Bolt(
                    tenant_id=ctx.tenant_id,
                    joint_id=joint.id,
                    bolt_no=bolt_no,
                    target_torque=record["target_torque"],
                    target_angle=None,
                    result=BoltResult.MISSING,
                )
            )
            bolts_created += 1

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="WORK_ORDER_UPLOAD",
        actor_user_id=ctx.user_id,
        resource_type="WorkOrder",
        resource_id=work_order.id,
        description=f"Uploaded work order file {file.filename}",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()

    return WorkOrderUploadResult(
        work_order_id=work_order.id,
        joints_created=joints_created,
        bolts_created=bolts_created,
        source_filename=file.filename or "",
    )
