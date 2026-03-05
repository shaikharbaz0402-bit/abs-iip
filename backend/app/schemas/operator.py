from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OperatorCreate(BaseModel):
    operator_code: str
    name: str


class OperatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    operator_code: str
    name: str
    jobs_completed: int
    error_rate: float
    avg_torque_deviation: float
