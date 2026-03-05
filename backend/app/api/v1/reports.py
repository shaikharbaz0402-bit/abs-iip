from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read, tenant_context_write
from app.core.config import get_settings
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.report import Report
from app.schemas.report import ReportGenerateRequest, ReportOut
from app.services.audit import log_event
from app.services.reporting import generate_pdf_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportOut)
def generate_report(
    payload: ReportGenerateRequest,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_write),
) -> ReportOut:
    base_url = str(request.base_url).rstrip("/")
    report = generate_pdf_report(
        db,
        tenant_id=ctx.tenant_id,
        report_type=payload.report_type,
        generated_by_user_id=ctx.user_id,
        base_verify_url=base_url,
        project_id=payload.project_id,
        work_order_id=payload.work_order_id,
        joint_id=payload.joint_id,
    )

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="REPORT_GENERATED",
        actor_user_id=ctx.user_id,
        resource_type="Report",
        resource_id=report.id,
        description=f"Generated report {report.report_type.value}",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(report)
    return ReportOut.model_validate(report)


@router.get("", response_model=list[ReportOut])
def list_reports(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[ReportOut]:
    rows = db.scalars(
        select(Report).where(Report.tenant_id == ctx.tenant_id).order_by(Report.created_at.desc())
    ).all()
    return [ReportOut.model_validate(item) for item in rows]


@router.get("/{report_id}/download")
def download_report(
    report_id: str,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
):
    report = db.scalar(select(Report).where(Report.id == report_id, Report.tenant_id == ctx.tenant_id))
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="REPORT_DOWNLOADED",
        actor_user_id=ctx.user_id,
        resource_type="Report",
        resource_id=report.id,
        description="Report downloaded",
        ip_address=request.client.host if request.client else None,
    )
    db.commit()

    return FileResponse(report.file_path, filename=f"report_{report.id}.pdf", media_type="application/pdf")
