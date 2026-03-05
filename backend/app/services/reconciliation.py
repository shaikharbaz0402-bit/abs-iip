from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.ai_alert import AIAlert
from app.models.bolt import Bolt
from app.models.enums import BoltResult, JointStatus, NotificationSeverity, NotificationType
from app.models.execution import Execution
from app.models.joint import Joint
from app.models.notification import Notification
from app.models.tool import Operator, Tool
from app.services.parser import parse_execution_file, sha256_bytes


def _torque_limits(target: float, tolerance: float) -> tuple[float, float]:
    tol = abs(float(tolerance or 0.0))
    delta = target * tol if tol <= 1 else tol
    return target - delta, target + delta


def _get_or_create_tool(db: Session, tenant_id: str, tool_code: str) -> Tool | None:
    tool_code = tool_code.strip()
    if not tool_code:
        return None
    tool = db.scalar(select(Tool).where(Tool.tenant_id == tenant_id, Tool.tool_code == tool_code))
    if tool is None:
        tool = Tool(tenant_id=tenant_id, tool_code=tool_code, model="Unknown")
        db.add(tool)
        db.flush()
    return tool


def _get_or_create_operator(db: Session, tenant_id: str, operator_code: str) -> Operator | None:
    operator_code = operator_code.strip()
    if not operator_code:
        return None
    operator = db.scalar(
        select(Operator).where(Operator.tenant_id == tenant_id, Operator.operator_code == operator_code)
    )
    if operator is None:
        operator = Operator(tenant_id=tenant_id, operator_code=operator_code, name=operator_code)
        db.add(operator)
        db.flush()
    return operator


def _joint_by_vin(
    db: Session,
    tenant_id: str,
    vin: str,
    work_order_id: str | None = None,
) -> Joint | None:
    if not vin:
        return None
    stmt = select(Joint).where(Joint.tenant_id == tenant_id, Joint.assigned_vin == vin)
    if work_order_id:
        stmt = stmt.where(Joint.work_order_id == work_order_id)
    return db.scalar(stmt)


def reconcile_execution_upload(
    db: Session,
    *,
    tenant_id: str,
    source_filename: str,
    file_bytes: bytes,
    work_order_id: str | None = None,
) -> dict[str, Any]:
    parsed = parse_execution_file(file_bytes=file_bytes, filename=source_filename)
    vin = parsed.get("vin") or ""
    rows = parsed["rows"]

    joint = _joint_by_vin(db, tenant_id=tenant_id, vin=vin, work_order_id=work_order_id)
    if joint is None:
        raise ValueError("No matching joint assignment found for uploaded VIN.")

    digest = sha256_bytes(file_bytes)

    bolt_map = {
        bolt.bolt_no: bolt
        for bolt in db.scalars(
            select(Bolt).where(Bolt.tenant_id == tenant_id, Bolt.joint_id == joint.id)
        ).all()
    }

    if not bolt_map:
        for bolt_no in range(1, joint.bolt_count + 1):
            bolt = Bolt(
                tenant_id=tenant_id,
                joint_id=joint.id,
                bolt_no=bolt_no,
                target_torque=joint.target_torque,
                target_angle=None,
                result=BoltResult.MISSING,
            )
            db.add(bolt)
        db.flush()
        bolt_map = {
            bolt.bolt_no: bolt
            for bolt in db.scalars(
                select(Bolt).where(Bolt.tenant_id == tenant_id, Bolt.joint_id == joint.id)
            ).all()
        }

    tool_cycle_delta: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "ok": 0, "nok": 0})
    operator_dev: dict[str, list[float]] = defaultdict(list)

    lower, upper = _torque_limits(joint.target_torque, joint.torque_tolerance)

    for row in rows:
        bolt_no = int(row["bolt_no"])
        bolt = bolt_map.get(bolt_no)
        if bolt is None:
            bolt = Bolt(
                tenant_id=tenant_id,
                joint_id=joint.id,
                bolt_no=bolt_no,
                target_torque=joint.target_torque,
                target_angle=None,
                result=BoltResult.MISSING,
            )
            db.add(bolt)
            db.flush()
            bolt_map[bolt_no] = bolt

        actual_torque = row.get("actual_torque")
        actual_angle = row.get("actual_angle")
        upstream_status = str(row.get("status") or "").upper()

        if actual_torque is None:
            result = BoltResult.MISSING
        else:
            in_range = lower <= float(actual_torque) <= upper
            if upstream_status == "OK" and in_range:
                result = BoltResult.OK
            elif in_range:
                result = BoltResult.NOK
            else:
                result = BoltResult.OUT_OF_TOLERANCE

        bolt.result = result

        tool = _get_or_create_tool(db, tenant_id, row.get("tool_code", ""))
        operator = _get_or_create_operator(db, tenant_id, row.get("operator_code", ""))

        source_key = f"{digest}:{int(row['row_index']) + 1}"

        existing = db.scalar(
            select(Execution).where(Execution.tenant_id == tenant_id, Execution.source_key == source_key)
        )
        if existing is not None:
            continue

        execution = Execution(
            tenant_id=tenant_id,
            project_id=joint.project_id,
            work_order_id=joint.work_order_id,
            joint_id=joint.id,
            bolt_id=bolt.id,
            timestamp=row["timestamp"],
            bolt_no=bolt_no,
            actual_torque=actual_torque,
            actual_angle=actual_angle,
            status=result,
            tool_id=tool.id if tool else None,
            operator_id=operator.id if operator else None,
            source_file=source_filename,
            source_key=source_key,
            metadata_json={
                "sheet_name": row.get("sheet_name"),
                "row_index": row.get("row_index"),
                "vin": vin,
            },
        )
        db.add(execution)

        if tool is not None:
            tool_cycle_delta[tool.id]["total"] += 1
            if result == BoltResult.OK:
                tool_cycle_delta[tool.id]["ok"] += 1
            else:
                tool_cycle_delta[tool.id]["nok"] += 1

        if operator is not None and actual_torque is not None:
            operator_dev[operator.id].append(abs(float(actual_torque) - joint.target_torque))

    db.flush()

    latest_per_bolt = {
        row.bolt_no: row
        for row in db.scalars(
            select(Execution)
            .where(Execution.tenant_id == tenant_id, Execution.joint_id == joint.id)
            .order_by(Execution.timestamp.asc(), Execution.created_at.asc())
        ).all()
    }

    ok = 0
    nok = 0
    missing = 0

    for bolt_no in range(1, joint.bolt_count + 1):
        latest = latest_per_bolt.get(bolt_no)
        if latest is None:
            missing += 1
            if bolt_no in bolt_map:
                bolt_map[bolt_no].result = BoltResult.MISSING
            continue

        if latest.status == BoltResult.OK:
            ok += 1
            bolt_map[bolt_no].result = BoltResult.OK
        elif latest.status == BoltResult.MISSING:
            missing += 1
            bolt_map[bolt_no].result = BoltResult.MISSING
        else:
            nok += 1
            bolt_map[bolt_no].result = latest.status

    if ok == joint.bolt_count:
        joint.status = JointStatus.CERTIFIED
    elif nok > 0:
        joint.status = JointStatus.REWORK_REQUIRED
    elif ok > 0:
        joint.status = JointStatus.IN_PROGRESS
    else:
        joint.status = JointStatus.PENDING

    for tool_id, delta in tool_cycle_delta.items():
        tool = db.get(Tool, tool_id)
        if tool is None:
            continue
        tool.total_cycles += delta["total"]
        tool.ok_cycles += delta["ok"]
        tool.nok_cycles += delta["nok"]

        nok_ratio = (tool.nok_cycles / tool.total_cycles) if tool.total_cycles else 0.0
        if nok_ratio > 0.25:
            tool.health_status = "Critical"
        elif nok_ratio > 0.1:
            tool.health_status = "Warning"
        else:
            tool.health_status = "Healthy"

    for operator_id, deviations in operator_dev.items():
        operator = db.get(Operator, operator_id)
        if operator is None:
            continue
        operator.jobs_completed += len(deviations)

        previous_jobs = max(operator.jobs_completed - len(deviations), 0)
        weighted_prev = operator.avg_torque_deviation * previous_jobs
        operator.avg_torque_deviation = (weighted_prev + sum(deviations)) / operator.jobs_completed

        if operator.jobs_completed:
            non_ok = db.scalar(
                select(func.count(Execution.id)).where(
                    and_(
                        Execution.tenant_id == tenant_id,
                        Execution.operator_id == operator_id,
                        Execution.status != BoltResult.OK,
                    )
                )
            )
            operator.error_rate = round((float(non_ok or 0) / operator.jobs_completed) * 100, 2)
        else:
            operator.error_rate = 0.0

    if nok > 0:
        db.add(
            Notification(
                tenant_id=tenant_id,
                notification_type=NotificationType.JOINT_FAILURE,
                severity=NotificationSeverity.CRITICAL,
                title="Joint requires rework",
                message=f"Joint {joint.joint_id} has {nok} non-compliant bolts.",
                project_id=joint.project_id,
                joint_id=joint.id,
            )
        )

    for tool_id, delta in tool_cycle_delta.items():
        if delta["nok"] < 3:
            continue
        db.add(
            AIAlert(
                tenant_id=tenant_id,
                alert_type="TOOL_MALFUNCTION_INDICATOR",
                severity="HIGH",
                message=f"Tool generated {delta['nok']} NOK cycles in latest batch.",
                project_id=joint.project_id,
                joint_id=joint.id,
                tool_id=tool_id,
            )
        )
        db.add(
            Notification(
                tenant_id=tenant_id,
                notification_type=NotificationType.TOOL_ANOMALY,
                severity=NotificationSeverity.WARNING,
                title="Tool anomaly detected",
                message=f"Tool may require inspection due to repeated NOK cycles.",
                project_id=joint.project_id,
                joint_id=joint.id,
                tool_id=tool_id,
            )
        )

    db.flush()

    return {
        "synced": True,
        "joint_id": joint.joint_id,
        "source_file": source_filename,
        "ok_bolts": ok,
        "nok_bolts": nok,
        "missing_bolts": missing,
        "updated_joint_status": joint.status.value,
    }

