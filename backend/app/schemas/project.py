from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class SiteCreate(BaseModel):
    name: str
    location: str


class SiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    location: str


class ProjectCreate(BaseModel):
    name: str
    client_name: str
    location: str
    start_date: date
    expected_completion: date
    site_id: str | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    client_name: str
    location: str
    start_date: date
    expected_completion: date
    status: str
    site_id: str | None = None
