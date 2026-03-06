import { apiClient } from "@/api/apiClient";
import type {
  AuditLog,
  Bolt,
  Branding,
  ClientProgress,
  DashboardAnalytics,
  Execution,
  ExecutionUploadResult,
  Joint,
  Notification,
  Operator,
  Plan,
  Project,
  Report,
  ReportRequest,
  Site,
  Subscription,
  Tenant,
  TokenResponse,
  Tool,
  UserCreatePayload,
  UserProfile,
  WorkOrder,
  WorkOrderUploadResult,
} from "@/types/domain";

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<TokenResponse>(
      "/auth/login",
      {
        email,
        password,
      },
      {
        skipAuth: true,
      },
    ),
  me: () => apiClient.get<UserProfile>("/auth/me"),
  createUser: (payload: UserCreatePayload) => apiClient.post<UserProfile>("/auth/users", payload),
};

export const usersApi = {
  list: () => apiClient.get<UserProfile[]>("/users"),
};

export const tenantsApi = {
  list: () => apiClient.get<Tenant[]>("/tenants"),
  create: (payload: { name: string; slug: string; contact_email: string }) => apiClient.post<Tenant>("/tenants", payload),
};

export const projectsApi = {
  list: () => apiClient.get<Project[]>("/projects"),
  create: (payload: {
    name: string;
    client_name: string;
    location: string;
    start_date: string;
    expected_completion: string;
    site_id?: string | null;
  }) => apiClient.post<Project>("/projects", payload),
  listSites: () => apiClient.get<Site[]>("/projects/sites"),
  createSite: (payload: { name: string; location: string }) => apiClient.post<Site>("/projects/sites", payload),
};

export const workOrdersApi = {
  list: (projectId?: string) =>
    apiClient.get<WorkOrder[]>("/work-orders", {
      query: { project_id: projectId },
    }),
  upload: (
    payload: { projectId: string; code: string; name: string; file: File },
    onProgress?: (percent: number) => void,
  ) => {
    const formData = new FormData();
    formData.append("project_id", payload.projectId);
    formData.append("code", payload.code);
    formData.append("name", payload.name);
    formData.append("file", payload.file);

    return apiClient.upload<WorkOrderUploadResult>({
      path: "/work-orders/upload",
      formData,
      onProgress,
    });
  },
};

export const jointsApi = {
  list: (projectId?: string, workOrderId?: string) =>
    apiClient.get<Joint[]>("/joints", {
      query: {
        project_id: projectId,
        work_order_id: workOrderId,
      },
    }),
  byId: (jointId: string) => apiClient.get<Joint>(`/joints/${jointId}`),
  assignVin: (jointId: string, payload: { assigned_vin: string; assigned_tool_id?: string | null }) =>
    apiClient.patch<Joint>(`/joints/${jointId}/assign-vin`, payload),
  layout: (jointId: string) =>
    apiClient.get<{
      joint_id: string;
      bolt_count: number;
      nodes: Array<{ bolt_no: number; x: number; y: number; color: string; status: string }>;
    }>(`/joints/${jointId}/layout`),
};

export const boltsApi = {
  list: (jointId: string) =>
    apiClient.get<Bolt[]>("/bolts", {
      query: {
        joint_id: jointId,
      },
    }),
};

export const executionsApi = {
  list: (filters?: { projectId?: string; jointId?: string }) =>
    apiClient.get<Execution[]>("/executions", {
      query: {
        project_id: filters?.projectId,
        joint_id: filters?.jointId,
      },
    }),
  upload: (payload: { file: File; workOrderId?: string }, onProgress?: (percent: number) => void) => {
    const formData = new FormData();
    formData.append("file", payload.file);
    if (payload.workOrderId) {
      formData.append("work_order_id", payload.workOrderId);
    }

    return apiClient.upload<ExecutionUploadResult>({
      path: "/executions/upload",
      formData,
      onProgress,
    });
  },
};

export const toolsApi = {
  list: () => apiClient.get<Tool[]>("/tools"),
  create: (payload: { tool_code: string; model: string; calibration_date?: string | null }) =>
    apiClient.post<Tool>("/tools", payload),
};

export const operatorsApi = {
  list: () => apiClient.get<Operator[]>("/operators"),
  create: (payload: { operator_code: string; name: string }) => apiClient.post<Operator>("/operators", payload),
};

export const analyticsApi = {
  dashboard: (projectId?: string) =>
    apiClient.get<DashboardAnalytics>("/analytics/dashboard", {
      query: {
        project_id: projectId,
      },
    }),
};

export const dashboardApi = {
  clientProgress: (projectId?: string) =>
    apiClient.get<ClientProgress>("/dashboard/client-progress", {
      query: {
        project_id: projectId,
      },
    }),
};

export const reportsApi = {
  list: () => apiClient.get<Report[]>("/reports"),
  create: (payload: ReportRequest) => apiClient.post<Report>("/reports", payload),
  downloadUrl: (reportId: string) => {
    const base = import.meta.env.VITE_API_BASE_URL || "https://abs-iip-production.up.railway.app";
    return `${base.replace(/\/$/, "")}/api/v1/reports/${reportId}/download`;
  },
};

export const notificationsApi = {
  list: (unreadOnly = false) =>
    apiClient.get<Notification[]>("/notifications", {
      query: { unread_only: unreadOnly },
    }),
  markRead: (notificationId: string, isRead: boolean) =>
    apiClient.patch<Notification>(`/notifications/${notificationId}`, { is_read: isRead }),
};

export const billingApi = {
  plans: () => apiClient.get<Plan[]>("/billing/plans"),
  subscription: () => apiClient.get<Subscription>("/billing/subscription"),
  updateSubscription: (payload: {
    tenant_id: string;
    plan_name: "Basic" | "Professional" | "Enterprise";
    status: "ACTIVE" | "PAUSED" | "CANCELLED";
  }) => apiClient.put<Subscription>("/billing/subscription", payload),
};

export const brandingApi = {
  get: () => apiClient.get<Branding | null>("/branding"),
  update: (payload: {
    client_display_name: string;
    primary_color: string;
    secondary_color: string;
    company_logo_path?: string | null;
  }) => apiClient.put<Branding>("/branding", payload),
};

export const auditApi = {
  list: (eventType?: string) =>
    apiClient.get<AuditLog[]>("/audit-logs", {
      query: {
        event_type: eventType,
      },
    }),
};
