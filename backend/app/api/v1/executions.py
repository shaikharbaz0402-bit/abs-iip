from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read, tenant_context_write
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.execution import Execution
from app.schemas.execution import ExecutionOut, ExecutionUploadResult
from app.services.ai_monitor import run_quality_monitor
from app.services.audit import log_event
from app.services.billing import register_usage
from app.services.reconciliation import reconcile_execution_upload
from app.services.websocket_manager import ws_manager

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("", response_model=list[ExecutionOut])
def list_executions(
    project_id: str | None = None,
    joint_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[ExecutionOut]:
    stmt = select(Execution).where(Execution.tenant_id == ctx.tenant_id)
    if project_id:
        stmt = stmt.where(Execution.project_id == project_id)
    if joint_id:
        stmt = stmt.where(Execution.joint_id == joint_id)

    rows = db.scalars(stmt.order_by(Execution.timestamp.desc()).limit(2000)).all()
    return [ExecutionOut.model_validate(item) for item in rows]


@router.post("/upload", response_model=ExecutionUploadResult)
async def upload_execution_file(
    request: Request,
    file: UploadFile = File(...),
    work_order_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_write),
) -> ExecutionUploadResult:
    file_bytes = await file.read()

    try:
        result = reconcile_execution_upload(
            db,
            tenant_id=ctx.tenant_id,
            source_filename=file.filename or "execution.xlsx",
            file_bytes=file_bytes,
            work_order_id=work_order_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    register_usage(db, ctx.tenant_id, amount=len(file_bytes))
    run_quality_monitor(db, ctx.tenant_id)

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="EXECUTION_UPLOAD",
        actor_user_id=ctx.user_id,
        resource_type="ExecutionBatch",
        resource_id=None,
        description=f"Execution file {file.filename} processed for joint {result['joint_id']}",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()

    await ws_manager.broadcast(
        ctx.tenant_id,
        {
            "event": "execution_upload_processed",
            "joint_id": result["joint_id"],
            "status": result["updated_joint_status"],
            "ok_bolts": result["ok_bolts"],
            "nok_bolts": result["nok_bolts"],
            "missing_bolts": result["missing_bolts"],
        },
    )

    return ExecutionUploadResult(**result)
