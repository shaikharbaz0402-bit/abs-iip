from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class WorkOrderCreate(BaseModel):
    project_id: str
    code: str
    name: str


class WorkOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    project_id: str
    code: str
    name: str
    source_filename: str
    source_hash: str


class WorkOrderUploadResult(BaseModel):
    work_order_id: str
    joints_created: int
    bolts_created: int
    source_filename: str
