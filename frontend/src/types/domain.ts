export type UserRole =
  | "SUPER_ADMIN"
  | "ABS_ENGINEER"
  | "CLIENT_ADMIN"
  | "CLIENT_ENGINEER"
  | "CLIENT_VIEWER";

export type PortalKind = "admin" | "manager" | "operator" | "client";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface UserCreatePayload {
  email: string;
  full_name: string;
  password: string;
  role: UserRole;
  tenant_id?: string | null;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  contact_email: string;
  is_active: boolean;
  created_at: string;
}

export interface Site {
  id: string;
  tenant_id: string;
  name: string;
  location: string;
}

export interface Project {
  id: string;
  tenant_id: string;
  name: string;
  client_name: string;
  location: string;
  start_date: string;
  expected_completion: string;
  status: string;
  site_id: string | null;
}

export interface WorkOrder {
  id: string;
  tenant_id: string;
  project_id: string;
  code: string;
  name: string;
  source_filename: string;
  source_hash: string;
}

export interface WorkOrderUploadResult {
  work_order_id: string;
  joints_created: number;
  bolts_created: number;
  source_filename: string;
}

export interface Joint {
  id: string;
  tenant_id: string;
  project_id: string;
  work_order_id: string;
  joint_id: string;
  bolt_count: number;
  target_torque: number;
  torque_tolerance: number;
  angle_tolerance: number;
  status: string;
  assigned_vin: string | null;
  assigned_tool_id: string | null;
}

export interface Bolt {
  id: string;
  tenant_id: string;
  joint_id: string;
  bolt_no: number;
  target_torque: number;
  target_angle: number | null;
  result: "OK" | "NOK" | "Missing" | "OutOfTolerance";
}

export interface Execution {
  id: string;
  tenant_id: string;
  project_id: string;
  work_order_id: string;
  joint_id: string;
  bolt_id: string | null;
  bolt_no: number;
  actual_torque: number | null;
  actual_angle: number | null;
  status: "OK" | "NOK" | "Missing" | "OutOfTolerance";
  source_file: string;
}

export interface ExecutionUploadResult {
  synced: boolean;
  joint_id: string;
  source_file: string;
  ok_bolts: number;
  nok_bolts: number;
  missing_bolts: number;
  updated_joint_status: string;
}

export interface KPIResponse {
  total_joints: number;
  certified_joints: number;
  pending_joints: number;
  completion_percentage: number;
  fpy: number;
}

export interface ToolHealthPoint {
  tool_code: string;
  total_cycles: number;
  ok_cycles: number;
  nok_cycles: number;
  health_status: string;
}

export interface OperatorAnalyticsPoint {
  operator_code: string;
  name: string;
  jobs_completed: number;
  error_rate: number;
  avg_torque_deviation: number;
}

export interface DashboardAnalytics {
  kpis: KPIResponse;
  torque_vs_angle: Array<Record<string, string | number | null>>;
  torque_distribution: Array<Record<string, string | number | null>>;
  compliance_heatmap: Array<Record<string, string | number | null>>;
  joint_completion: Array<Record<string, string | number | null>>;
  tool_health: ToolHealthPoint[];
  operator_analytics: OperatorAnalyticsPoint[];
  ai_warnings: Array<Record<string, string | number | null>>;
}

export interface ClientProgress {
  total_joints: number;
  certified_joints: number;
  completion_percentage: number;
  items: Array<{
    joint_id: string;
    status: string;
    project_id: string;
  }>;
}

export interface Tool {
  id: string;
  tenant_id: string;
  tool_code: string;
  model: string;
  total_cycles: number;
  ok_cycles: number;
  nok_cycles: number;
  calibration_date: string | null;
  health_status: string;
}

export interface Operator {
  id: string;
  tenant_id: string;
  operator_code: string;
  name: string;
  jobs_completed: number;
  error_rate: number;
  avg_torque_deviation: number;
}

export interface Notification {
  id: string;
  tenant_id: string;
  notification_type: "JOINT_FAILURE" | "TOOL_ANOMALY" | "CALIBRATION_DUE" | "MILESTONE";
  severity: "INFO" | "WARNING" | "CRITICAL";
  title: string;
  message: string;
  is_read: boolean;
  project_id: string | null;
  joint_id: string | null;
  tool_id: string | null;
}

export interface Plan {
  id: string;
  name: "Basic" | "Professional" | "Enterprise";
  monthly_price: number;
  seat_limit: number;
  usage_limit: number;
}

export interface Subscription {
  id: string;
  tenant_id: string;
  plan_id: string;
  status: "ACTIVE" | "PAUSED" | "CANCELLED";
  seats_used: number;
  current_month_usage: number;
}

export interface Branding {
  id: string;
  tenant_id: string;
  client_display_name: string;
  primary_color: string;
  secondary_color: string;
  company_logo_path: string | null;
}

export interface AuditLog {
  id: string;
  tenant_id: string;
  event_type: string;
  actor_user_id: string | null;
  resource_type: string;
  resource_id: string | null;
  description: string;
  ip_address: string | null;
  created_at: string;
}

export interface Report {
  id: string;
  tenant_id: string;
  report_type: "Joint Certification Report" | "Work Order Report" | "Project Quality Report";
  project_id: string | null;
  work_order_id: string | null;
  joint_id: string | null;
  file_path: string;
  qr_token: string;
}

export interface ReportRequest {
  report_type: "Joint Certification Report" | "Work Order Report" | "Project Quality Report";
  project_id?: string;
  work_order_id?: string;
  joint_id?: string;
}

export interface DashboardRealtimeEvent {
  event: string;
  joint_id?: string;
  status?: string;
  ok_bolts?: number;
  nok_bolts?: number;
  missing_bolts?: number;
}

export interface PlatformSettings {
  compact_navigation: boolean;
  realtime_auto_refresh: boolean;
  dashboard_animations: boolean;
  sound_alerts: boolean;
  primary_font: "Segoe UI" | "Inter" | "IBM Plex Sans";
  preferred_chart_theme: "executive" | "classic" | "contrast";
  landing_module: "dashboard" | "tenants" | "projects" | "analytics";
}
