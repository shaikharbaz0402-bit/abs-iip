from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.enums import BoltResult


class BoltOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    joint_id: str
    bolt_no: int
    target_torque: float
    target_angle: float | None
    result: BoltResult


class BoltDetail(BaseModel):
    bolt_no: int
    status: BoltResult
    target_torque: float
    actual_torque: float | None
    actual_angle: float | None
    deviation: float | None
