from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(ORMModel):
    message: str


class Pagination(ORMModel):
    total: int
    page: int
    page_size: int


class HealthResponse(ORMModel):
    status: str
    timestamp: datetime
