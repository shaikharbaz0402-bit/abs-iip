from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.enums import PlanType, SubscriptionStatus


class SubscriptionUpdate(BaseModel):
    tenant_id: str
    plan_name: PlanType
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    plan_id: str
    status: SubscriptionStatus
    seats_used: int
    current_month_usage: int


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: PlanType
    monthly_price: float
    seat_limit: int
    usage_limit: int
