from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class ToolCreate(BaseModel):
    tool_code: str
    model: str
    calibration_date: date | None = None


class ToolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    tool_code: str
    model: str
    total_cycles: int
    ok_cycles: int
    nok_cycles: int
    calibration_date: date | None
    health_status: str
