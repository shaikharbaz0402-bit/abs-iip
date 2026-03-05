from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BoltResult


class ExecutionRow(BaseModel):
    timestamp: datetime
    bolt_no: int
    actual_torque: float | None = None
    actual_angle: float | None = None
    status: BoltResult | None = None
    tool_code: str | None = None
    operator_code: str | None = None


class ExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    project_id: str
    work_order_id: str
    joint_id: str
    bolt_id: str | None
    bolt_no: int
    actual_torque: float | None
    actual_angle: float | None
    status: BoltResult
    source_file: str


class ExecutionUploadResult(BaseModel):
    synced: bool
    joint_id: str
    source_file: str
    ok_bolts: int
    nok_bolts: int
    missing_bolts: int
    updated_joint_status: str
