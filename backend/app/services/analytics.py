from __future__ import annotations

from collections import defaultdict

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.ai_alert import AIAlert
from app.models.enums import BoltResult, JointStatus
from app.models.execution import Execution
from app.models.joint import Joint
from app.models.tool import Operator, Tool


def build_dashboard_analytics(db: Session, tenant_id: str, project_id: str | None = None) -> dict:
    joint_stmt = select(Joint).where(Joint.tenant_id == tenant_id)
    exec_stmt = select(Execution).where(Execution.tenant_id == tenant_id)
    tool_stmt = select(Tool).where(Tool.tenant_id == tenant_id)
    operator_stmt = select(Operator).where(Operator.tenant_id == tenant_id)
    ai_stmt = select(AIAlert).where(AIAlert.tenant_id == tenant_id, AIAlert.is_resolved.is_(False))

    if project_id:
        joint_stmt = joint_stmt.where(Joint.project_id == project_id)
        exec_stmt = exec_stmt.where(Execution.project_id == project_id)
        ai_stmt = ai_stmt.where(AIAlert.project_id == project_id)

    joints = db.scalars(joint_stmt).all()
    executions = db.scalars(exec_stmt.order_by(Execution.timestamp.asc())).all()
    tools = db.scalars(tool_stmt).all()
    operators = db.scalars(operator_stmt).all()
    ai_alerts = db.scalars(ai_stmt).all()

    total_joints = len(joints)
    certified = sum(1 for joint in joints if joint.status == JointStatus.CERTIFIED)
    pending = sum(1 for joint in joints if joint.status == JointStatus.PENDING)
    completion_pct = round((certified / total_joints) * 100, 2) if total_joints else 0.0

    first_pass_map: dict[tuple[str, int], Execution] = {}
    latest_map: dict[tuple[str, int], Execution] = {}

    for exe in executions:
        key = (exe.joint_id, exe.bolt_no)
        if key not in first_pass_map:
            first_pass_map[key] = exe
        latest_map[key] = exe

    first_total = len(first_pass_map)
    first_ok = sum(1 for item in first_pass_map.values() if item.status == BoltResult.OK)
    fpy = round((first_ok / first_total) * 100, 2) if first_total else 0.0

    torque_vs_angle = [
        {
            "joint_id": exe.joint_id,
            "bolt_no": exe.bolt_no,
            "actual_torque": exe.actual_torque,
            "actual_angle": exe.actual_angle,
            "status": exe.status.value,
            "timestamp": exe.timestamp.isoformat(),
        }
        for exe in executions
        if exe.actual_torque is not None
    ]

    distribution = defaultdict(int)
    for exe in executions:
        if exe.actual_torque is None:
            continue
        bucket = round(float(exe.actual_torque) / 10) * 10
        distribution[str(int(bucket))] += 1
    torque_distribution = [
        {"bucket": bucket, "count": count}
        for bucket, count in sorted(distribution.items(), key=lambda item: int(item[0]))
    ]

    compliance_heatmap = [
        {
            "joint_id": key[0],
            "bolt_no": key[1],
            "status": value.status.value,
        }
        for key, value in latest_map.items()
    ]

    joint_completion = []
    for joint in joints:
        joint_bolts = [
            item for key, item in latest_map.items() if key[0] == joint.id and 1 <= key[1] <= joint.bolt_count
        ]
        ok_count = sum(1 for item in joint_bolts if item.status == BoltResult.OK)
        progress = round((ok_count / joint.bolt_count) * 100, 2) if joint.bolt_count else 0.0
        joint_completion.append(
            {
                "joint_id": joint.joint_id,
                "status": joint.status.value,
                "ok_bolts": ok_count,
                "bolt_count": joint.bolt_count,
                "completion": progress,
            }
        )

    tool_health = [
        {
            "tool_code": tool.tool_code,
            "total_cycles": tool.total_cycles,
            "ok_cycles": tool.ok_cycles,
            "nok_cycles": tool.nok_cycles,
            "health_status": tool.health_status,
        }
        for tool in tools
    ]

    operator_analytics = [
        {
            "operator_code": op.operator_code,
            "name": op.name,
            "jobs_completed": op.jobs_completed,
            "error_rate": op.error_rate,
            "avg_torque_deviation": op.avg_torque_deviation,
        }
        for op in operators
    ]

    ai_warnings = [
        {
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "joint_id": alert.joint_id,
            "tool_id": alert.tool_id,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        }
        for alert in ai_alerts
    ]

    return {
        "kpis": {
            "total_joints": total_joints,
            "certified_joints": certified,
            "pending_joints": pending,
            "completion_percentage": completion_pct,
            "fpy": fpy,
        },
        "torque_vs_angle": torque_vs_angle,
        "torque_distribution": torque_distribution,
        "compliance_heatmap": compliance_heatmap,
        "joint_completion": joint_completion,
        "tool_health": tool_health,
        "operator_analytics": operator_analytics,
        "ai_warnings": ai_warnings,
    }


def count_active_users(db: Session, tenant_id: str) -> int:
    from app.models.user import User

    return int(
        db.scalar(select(func.count(User.id)).where(and_(User.tenant_id == tenant_id, User.is_active.is_(True))))
        or 0
    )
