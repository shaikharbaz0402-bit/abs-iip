from __future__ import annotations

from pydantic import BaseModel


class KPIResponse(BaseModel):
    total_joints: int
    certified_joints: int
    pending_joints: int
    completion_percentage: float
    fpy: float


class ToolHealthPoint(BaseModel):
    tool_code: str
    total_cycles: int
    ok_cycles: int
    nok_cycles: int
    health_status: str


class OperatorAnalyticsPoint(BaseModel):
    operator_code: str
    name: str
    jobs_completed: int
    error_rate: float
    avg_torque_deviation: float


class DashboardAnalytics(BaseModel):
    kpis: KPIResponse
    torque_vs_angle: list[dict]
    torque_distribution: list[dict]
    compliance_heatmap: list[dict]
    joint_completion: list[dict]
    tool_health: list[ToolHealthPoint]
    operator_analytics: list[OperatorAnalyticsPoint]
    ai_warnings: list[dict]
