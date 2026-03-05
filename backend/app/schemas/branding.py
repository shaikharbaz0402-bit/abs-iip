from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BrandingUpdate(BaseModel):
    client_display_name: str
    primary_color: str
    secondary_color: str
    company_logo_path: str | None = None


class BrandingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    client_display_name: str
    primary_color: str
    secondary_color: str
    company_logo_path: str | None
