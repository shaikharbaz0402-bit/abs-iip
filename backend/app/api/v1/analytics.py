from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.schemas.analytics import DashboardAnalytics
from app.services.analytics import build_dashboard_analytics
from app.services.notifications import check_calibration_due, check_project_milestones

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardAnalytics)
def dashboard_analytics(
    project_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> DashboardAnalytics:
    check_calibration_due(db, ctx.tenant_id)
    check_project_milestones(db, ctx.tenant_id)
    payload = build_dashboard_analytics(db, tenant_id=ctx.tenant_id, project_id=project_id)
    db.commit()
    return DashboardAnalytics(**payload)
