from __future__ import annotations

from collections import Counter

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.ai_alert import AIAlert
from app.models.enums import BoltResult
from app.models.execution import Execution


def run_quality_monitor(db: Session, tenant_id: str, project_id: str | None = None) -> list[AIAlert]:
    stmt = select(Execution).where(Execution.tenant_id == tenant_id)
    if project_id:
        stmt = stmt.where(Execution.project_id == project_id)

    executions = db.scalars(stmt).all()
    alerts: list[AIAlert] = []

    # Pattern 1: repeated bolt failures by joint
    joint_failures = Counter(exe.joint_id for exe in executions if exe.status != BoltResult.OK)
    for joint_id, count in joint_failures.items():
        if count < 5:
            continue
        alerts.append(
            AIAlert(
                tenant_id=tenant_id,
                alert_type="REPEATED_BOLT_FAILURE",
                severity="MEDIUM",
                message=f"Joint {joint_id} has {count} non-OK executions.",
                project_id=project_id,
                joint_id=joint_id,
            )
        )

    # Pattern 2: torque deviation trend
    torque_devs = [
        abs(exe.actual_torque or 0.0)
        for exe in executions
        if exe.actual_torque is not None and exe.status == BoltResult.OUT_OF_TOLERANCE
    ]
    if len(torque_devs) >= 10:
        avg_dev = sum(torque_devs) / len(torque_devs)
        if avg_dev > 30:
            alerts.append(
                AIAlert(
                    tenant_id=tenant_id,
                    alert_type="TORQUE_DEVIATION_PATTERN",
                    severity="HIGH",
                    message=f"Average torque deviation trend is high: {avg_dev:.2f}",
                    project_id=project_id,
                )
            )

    for alert in alerts:
        duplicate = db.scalar(
            select(AIAlert).where(
                and_(
                    AIAlert.tenant_id == alert.tenant_id,
                    AIAlert.alert_type == alert.alert_type,
                    AIAlert.joint_id == alert.joint_id,
                    AIAlert.is_resolved.is_(False),
                )
            )
        )
        if duplicate is None:
            db.add(alert)

    db.flush()

    return db.scalars(
        select(AIAlert).where(AIAlert.tenant_id == tenant_id, AIAlert.is_resolved.is_(False))
    ).all()
