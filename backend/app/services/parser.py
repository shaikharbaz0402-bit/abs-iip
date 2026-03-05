from __future__ import annotations

import csv
import hashlib
import io
import re
from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd

WORK_ORDER_ALIASES = {
    "joint_id": ["joint_id", "joint id", "joint", "joint no", "joint number"],
    "bolt_count": ["bolt_count", "bolt count", "target bolts", "bolts", "qty"],
    "target_torque": ["target_torque", "target torque", "torque target", "torque"],
    "torque_tolerance": ["torque_tolerance", "torque tolerance", "tolerance", "tol"],
    "angle_tolerance": ["angle_tolerance", "angle tolerance", "angle tol"],
    "assigned_vin": ["assigned_vin", "vin", "ags vin", "tool vin"],
}

EXEC_ALIASES = {
    "timestamp": ["timestamp", "time", "datetime", "date"],
    "bolt_no": ["bolt_no", "bolt", "bolt no", "position"],
    "actual_torque": ["actual_torque", "actual torque", "torque", "measured torque"],
    "actual_angle": ["actual_angle", "actual angle", "angle"],
    "status": ["status", "result", "ok/nok", "pass/fail"],
    "tool_code": ["tool_code", "tool", "tool serial", "tool id"],
    "operator_code": ["operator_code", "operator", "technician"],
    "vin": ["vin", "ags vin", "tool vin", "vin number"],
}

VIN_PATTERN = re.compile(r"\bVIN\b[^A-Z0-9]*([A-Z0-9\-]{5,})", flags=re.IGNORECASE)


def sha256_bytes(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def normalize_vin(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "").strip().upper())


def _resolve_columns(columns: list[str], aliases: dict[str, list[str]]) -> dict[str, str]:
    normalized = {column: normalize_text(column) for column in columns}
    resolved: dict[str, str] = {}

    for key, alias_list in aliases.items():
        alias_norm = [normalize_text(alias) for alias in alias_list]
        for column, norm in normalized.items():
            if norm in alias_norm:
                resolved[key] = column
                break
        if key not in resolved:
            for column, norm in normalized.items():
                if any(alias in norm for alias in alias_norm if alias):
                    resolved[key] = column
                    break

    return resolved


def parse_work_order_excel(file_bytes: bytes) -> list[dict[str, Any]]:
    sheets = pd.read_excel(BytesIO(file_bytes), sheet_name=None)
    records: list[dict[str, Any]] = []

    for _, df in sheets.items():
        if df.empty:
            continue
        resolved = _resolve_columns(list(df.columns), WORK_ORDER_ALIASES)
        if not {"joint_id", "bolt_count", "target_torque"}.issubset(resolved):
            continue

        for _, row in df.iterrows():
            joint_id = str(row.get(resolved["joint_id"], "")).strip()
            if not joint_id:
                continue

            try:
                bolt_count = int(float(row.get(resolved["bolt_count"])))
                target_torque = float(row.get(resolved["target_torque"]))
            except (TypeError, ValueError):
                continue

            torque_tolerance = row.get(resolved.get("torque_tolerance"), 0.05)
            angle_tolerance = row.get(resolved.get("angle_tolerance"), 0.0)
            assigned_vin = normalize_vin(row.get(resolved.get("assigned_vin"), ""))

            records.append(
                {
                    "joint_id": joint_id,
                    "bolt_count": bolt_count,
                    "target_torque": target_torque,
                    "torque_tolerance": float(torque_tolerance or 0.05),
                    "angle_tolerance": float(angle_tolerance or 0.0),
                    "assigned_vin": assigned_vin or None,
                }
            )

    if not records:
        raise ValueError("No valid work order rows found.")
    return records


def _extract_vin_from_df(df: pd.DataFrame) -> str:
    resolved = _resolve_columns(list(df.columns), EXEC_ALIASES)
    vin_column = resolved.get("vin")
    if vin_column:
        for value in df[vin_column].dropna().tolist():
            vin = normalize_vin(value)
            if vin:
                return vin

    for row in df.itertuples(index=False):
        for value in row:
            text = str(value or "")
            match = VIN_PATTERN.search(text)
            if match:
                return normalize_vin(match.group(1))
    return ""


def parse_execution_excel(file_bytes: bytes) -> dict[str, Any]:
    sheets = pd.read_excel(BytesIO(file_bytes), sheet_name=None)
    all_rows: list[dict[str, Any]] = []
    vin = ""

    for sheet_name, df in sheets.items():
        if df.empty:
            continue

        if not vin:
            vin = _extract_vin_from_df(df)

        resolved = _resolve_columns(list(df.columns), EXEC_ALIASES)
        if not {"actual_torque"}.issubset(resolved):
            continue

        for idx, row in df.iterrows():
            bolt_no_raw = row.get(resolved.get("bolt_no"))
            try:
                bolt_no = int(float(bolt_no_raw)) if bolt_no_raw is not None else idx + 1
            except (TypeError, ValueError):
                bolt_no = idx + 1

            torque_raw = row.get(resolved.get("actual_torque"))
            angle_raw = row.get(resolved.get("actual_angle"))
            timestamp_raw = row.get(resolved.get("timestamp"))

            try:
                torque = float(torque_raw) if torque_raw is not None else None
            except (TypeError, ValueError):
                torque = None

            try:
                angle = float(angle_raw) if angle_raw is not None else None
            except (TypeError, ValueError):
                angle = None

            ts = pd.to_datetime(timestamp_raw, errors="coerce")
            timestamp = ts.to_pydatetime() if not pd.isna(ts) else datetime.utcnow()

            status_raw = str(row.get(resolved.get("status"), "")).strip().upper()
            if status_raw in {"OK", "PASS", "PASSED"}:
                status = "OK"
            elif status_raw in {"NOK", "FAIL", "FAILED"}:
                status = "NOK"
            else:
                status = "OK"

            all_rows.append(
                {
                    "sheet_name": sheet_name,
                    "row_index": int(idx),
                    "timestamp": timestamp,
                    "bolt_no": bolt_no,
                    "actual_torque": torque,
                    "actual_angle": angle,
                    "status": status,
                    "tool_code": str(row.get(resolved.get("tool_code"), "") or "").strip(),
                    "operator_code": str(row.get(resolved.get("operator_code"), "") or "").strip(),
                }
            )

    if not all_rows:
        raise ValueError("No valid execution rows found.")

    return {
        "vin": normalize_vin(vin),
        "rows": all_rows,
    }


def parse_execution_csv(file_bytes: bytes) -> dict[str, Any]:
    text = file_bytes.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    columns = list(reader.fieldnames or [])
    resolved = _resolve_columns(columns, EXEC_ALIASES)

    rows: list[dict[str, Any]] = []
    vin = ""
    for idx, row in enumerate(reader, start=1):
        if not vin:
            vin = normalize_vin(row.get(resolved.get("vin"), ""))

        timestamp = pd.to_datetime(row.get(resolved.get("timestamp")), errors="coerce")
        dt = timestamp.to_pydatetime() if not pd.isna(timestamp) else datetime.utcnow()

        bolt_no_raw = row.get(resolved.get("bolt_no"))
        try:
            bolt_no = int(float(bolt_no_raw)) if bolt_no_raw else idx
        except (TypeError, ValueError):
            bolt_no = idx

        torque_raw = row.get(resolved.get("actual_torque"))
        angle_raw = row.get(resolved.get("actual_angle"))

        try:
            torque = float(torque_raw) if torque_raw not in (None, "") else None
        except (TypeError, ValueError):
            torque = None

        try:
            angle = float(angle_raw) if angle_raw not in (None, "") else None
        except (TypeError, ValueError):
            angle = None

        status_raw = str(row.get(resolved.get("status"), "")).strip().upper()
        status = "OK" if status_raw in {"OK", "PASS", "PASSED"} else "NOK"

        rows.append(
            {
                "sheet_name": "csv",
                "row_index": idx,
                "timestamp": dt,
                "bolt_no": bolt_no,
                "actual_torque": torque,
                "actual_angle": angle,
                "status": status,
                "tool_code": str(row.get(resolved.get("tool_code"), "") or "").strip(),
                "operator_code": str(row.get(resolved.get("operator_code"), "") or "").strip(),
            }
        )

    if not rows:
        raise ValueError("No execution rows found in CSV.")

    return {"vin": vin, "rows": rows}


def parse_execution_file(file_bytes: bytes, filename: str) -> dict[str, Any]:
    name = filename.lower()
    if name.endswith(".csv"):
        return parse_execution_csv(file_bytes)
    return parse_execution_excel(file_bytes)
