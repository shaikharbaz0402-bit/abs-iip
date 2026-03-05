from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    audit_logs,
    auth,
    billing,
    bolts,
    branding,
    dashboard,
    executions,
    joints,
    notifications,
    operators,
    projects,
    reports,
    tenants,
    tools,
    users,
    verify,
    work_orders,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(projects.router)
api_router.include_router(work_orders.router)
api_router.include_router(joints.router)
api_router.include_router(bolts.router)
api_router.include_router(executions.router)
api_router.include_router(tools.router)
api_router.include_router(operators.router)
api_router.include_router(analytics.router)
api_router.include_router(reports.router)
api_router.include_router(verify.router)
api_router.include_router(users.router)
api_router.include_router(branding.router)
api_router.include_router(notifications.router)
api_router.include_router(audit_logs.router)
api_router.include_router(billing.router)
api_router.include_router(dashboard.router)
