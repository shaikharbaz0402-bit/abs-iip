from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_admin, tenant_context_read
from app.core.deps import TenantContext
from app.db.session import get_db
from app.models.project import Project, Site
from app.schemas.project import ProjectCreate, ProjectOut, SiteCreate, SiteOut
from app.services.audit import log_event

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/sites", response_model=SiteOut)
def create_site(
    payload: SiteCreate,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_admin),
) -> SiteOut:
    site = Site(tenant_id=ctx.tenant_id, name=payload.name, location=payload.location)
    db.add(site)

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="SITE_CREATED",
        actor_user_id=ctx.user_id,
        resource_type="Site",
        resource_id=site.id,
        description=f"Site {payload.name} created",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(site)
    return SiteOut.model_validate(site)


@router.get("/sites", response_model=list[SiteOut])
def list_sites(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[SiteOut]:
    rows = db.scalars(select(Site).where(Site.tenant_id == ctx.tenant_id).order_by(Site.name.asc())).all()
    return [SiteOut.model_validate(item) for item in rows]


@router.post("", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_admin),
) -> ProjectOut:
    project = Project(
        tenant_id=ctx.tenant_id,
        name=payload.name,
        client_name=payload.client_name,
        location=payload.location,
        start_date=payload.start_date,
        expected_completion=payload.expected_completion,
        site_id=payload.site_id,
    )
    db.add(project)

    log_event(
        db,
        tenant_id=ctx.tenant_id,
        event_type="PROJECT_CREATED",
        actor_user_id=ctx.user_id,
        resource_type="Project",
        resource_id=project.id,
        description=f"Project {payload.name} created",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(project)
    return ProjectOut.model_validate(project)


@router.get("", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> list[ProjectOut]:
    rows = db.scalars(select(Project).where(Project.tenant_id == ctx.tenant_id).order_by(Project.created_at.desc())).all()
    return [ProjectOut.model_validate(item) for item in rows]
