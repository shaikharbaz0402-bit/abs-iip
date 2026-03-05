from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import JointStatus, NotificationSeverity, NotificationType
from app.models.joint import Joint
from app.models.notification import Notification
from app.models.project import Project
from app.models.tool import Tool


def create_notification(
    db: Session,
    *,
    tenant_id: str,
    notification_type: NotificationType,
    severity: NotificationSeverity,
    title: str,
    message: str,
    project_id: str | None = None,
    joint_id: str | None = None,
    tool_id: str | None = None,
) -> Notification:
    item = Notification(
        tenant_id=tenant_id,
        notification_type=notification_type,
        severity=severity,
        title=title,
        message=message,
        project_id=project_id,
        joint_id=joint_id,
        tool_id=tool_id,
    )
    db.add(item)
    db.flush()
    return item


def check_calibration_due(db: Session, tenant_id: str) -> int:
    threshold = date.today() + timedelta(days=7)
    tools = db.scalars(select(Tool).where(Tool.tenant_id == tenant_id)).all()

    created = 0
    for tool in tools:
        if tool.calibration_date is None:
            continue
        if tool.calibration_date > threshold:
            continue

        exists = db.scalar(
            select(Notification).where(
                Notification.tenant_id == tenant_id,
                Notification.tool_id == tool.id,
                Notification.notification_type == NotificationType.CALIBRATION_DUE,
                Notification.is_read.is_(False),
            )
        )
        if exists is not None:
            continue

        create_notification(
            db,
            tenant_id=tenant_id,
            notification_type=NotificationType.CALIBRATION_DUE,
            severity=NotificationSeverity.WARNING,
            title="Calibration due soon",
            message=f"Tool {tool.tool_code} calibration is due on {tool.calibration_date}.",
            tool_id=tool.id,
        )
        created += 1

    return created


def check_project_milestones(db: Session, tenant_id: str) -> int:
    created = 0
    thresholds = [25, 50, 75, 100]

    projects = db.scalars(select(Project).where(Project.tenant_id == tenant_id)).all()
    for project in projects:
        joints = db.scalars(select(Joint).where(Joint.tenant_id == tenant_id, Joint.project_id == project.id)).all()
        total = len(joints)
        if total == 0:
            continue

        certified = sum(1 for joint in joints if joint.status == JointStatus.CERTIFIED)
        completion = round((certified / total) * 100)

        achieved = [threshold for threshold in thresholds if completion >= threshold]
        if not achieved:
            continue

        threshold = max(achieved)
        marker = f"MILESTONE_{project.id}_{threshold}"

        exists = db.scalar(
            select(Notification).where(
                Notification.tenant_id == tenant_id,
                Notification.notification_type == NotificationType.MILESTONE,
                Notification.message.contains(marker),
            )
        )
        if exists is not None:
            continue

        create_notification(
            db,
            tenant_id=tenant_id,
            notification_type=NotificationType.MILESTONE,
            severity=NotificationSeverity.INFO,
            title="Project completion milestone",
            message=(
                f"{marker}: Project {project.name} reached {threshold}% certified joints "
                f"({certified}/{total})."
            ),
            project_id=project.id,
        )
        created += 1

    return created
