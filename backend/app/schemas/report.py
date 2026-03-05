from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.enums import ReportType


class ReportGenerateRequest(BaseModel):
    report_type: ReportType
    project_id: str | None = None
    work_order_id: str | None = None
    joint_id: str | None = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    report_type: ReportType
    project_id: str | None
    work_order_id: str | None
    joint_id: str | None
    file_path: str
    qr_token: str


class VerificationResponse(BaseModel):
    valid: bool
    tenant_name: str | None = None
    report_type: str | None = None
    joint_id: str | None = None
    project_name: str | None = None
    generated_at: str | None = None
