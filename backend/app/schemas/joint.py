from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.enums import JointStatus


class JointCreate(BaseModel):
    project_id: str
    work_order_id: str
    joint_id: str
    bolt_count: int
    target_torque: float
    torque_tolerance: float
    angle_tolerance: float = 0.0
    assigned_vin: str | None = None


class JointVINAssign(BaseModel):
    assigned_vin: str
    assigned_tool_id: str | None = None


class JointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    project_id: str
    work_order_id: str
    joint_id: str
    bolt_count: int
    target_torque: float
    torque_tolerance: float
    angle_tolerance: float
    status: JointStatus
    assigned_vin: str | None
    assigned_tool_id: str | None
