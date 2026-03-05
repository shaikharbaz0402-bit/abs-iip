from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ABS_ENGINEER = "ABS_ENGINEER"
    CLIENT_ADMIN = "CLIENT_ADMIN"
    CLIENT_ENGINEER = "CLIENT_ENGINEER"
    CLIENT_VIEWER = "CLIENT_VIEWER"


class JointStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    CERTIFIED = "Certified"
    REWORK_REQUIRED = "Rework Required"


class BoltResult(str, enum.Enum):
    OK = "OK"
    NOK = "NOK"
    MISSING = "Missing"
    OUT_OF_TOLERANCE = "OutOfTolerance"


class ReportType(str, enum.Enum):
    JOINT_CERTIFICATION = "Joint Certification Report"
    WORK_ORDER = "Work Order Report"
    PROJECT_QUALITY = "Project Quality Report"


class PlanType(str, enum.Enum):
    BASIC = "Basic"
    PROFESSIONAL = "Professional"
    ENTERPRISE = "Enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


class NotificationType(str, enum.Enum):
    JOINT_FAILURE = "JOINT_FAILURE"
    TOOL_ANOMALY = "TOOL_ANOMALY"
    CALIBRATION_DUE = "CALIBRATION_DUE"
    MILESTONE = "MILESTONE"


class NotificationSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
