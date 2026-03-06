import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/auth/AuthContext";
import { DataTable } from "@/components/data/DataTable";
import { FileDropzone } from "@/components/forms/FileDropzone";
import { LogoPicker } from "@/components/forms/LogoPicker";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Loader } from "@/components/ui/Loader";
import { ToggleSwitch } from "@/components/ui/ToggleSwitch";
import { FailureTrendChart } from "@/dashboards/FailureTrendChart";
import { JointHeatmap } from "@/dashboards/JointHeatmap";
import { KpiGrid } from "@/dashboards/KpiGrid";
import { OperatorPerformanceChart } from "@/dashboards/OperatorPerformanceChart";
import { RealtimeBanner } from "@/dashboards/RealtimeBanner";
import { ToolUsageChart } from "@/dashboards/ToolUsageChart";
import { TorqueAngleScatter } from "@/dashboards/TorqueAngleScatter";
import { TorqueDistributionChart } from "@/dashboards/TorqueDistributionChart";
import { useDashboardRealtime } from "@/hooks/useDashboardRealtime";
import { PortalLayout } from "@/layouts/PortalLayout";
import {
  analyticsApi,
  auditApi,
  authApi,
  billingApi,
  brandingApi,
  executionsApi,
  notificationsApi,
  operatorsApi,
  projectsApi,
  reportsApi,
  tenantsApi,
  toolsApi,
  usersApi,
  workOrdersApi,
} from "@/services/absApi";
import type {
  AuditLog,
  Branding,
  DashboardAnalytics,
  Execution,
  Notification,
  Operator,
  Plan,
  PlatformSettings,
  Project,
  Report,
  Subscription,
  Tenant,
  Tool,
  UserProfile,
  UserRole,
  WorkOrder,
} from "@/types/domain";
import { formatDate, formatDateTime, formatNumber } from "@/utils/format";

const navItems = [
  { id: "dashboard", label: "Dashboard" },
  { id: "tenants", label: "Tenants" },
  { id: "projects", label: "Projects" },
  { id: "workOrders", label: "Work Orders" },
  { id: "operators", label: "Operators" },
  { id: "tools", label: "Tools" },
  { id: "analytics", label: "Analytics" },
  { id: "reports", label: "Reports" },
  { id: "users", label: "Users" },
  { id: "billing", label: "Billing" },
  { id: "audit", label: "Audit Logs" },
  { id: "platformSettings", label: "Platform Settings" },
  { id: "branding", label: "Branding Settings" },
] as const;

type TabId = (typeof navItems)[number]["id"];

const ABS_ROLES: UserRole[] = ["SUPER_ADMIN", "ABS_ENGINEER"];

const PLATFORM_SETTINGS_KEY = "abs_iip_platform_settings";

const defaultPlatformSettings: PlatformSettings = {
  compact_navigation: false,
  realtime_auto_refresh: true,
  dashboard_animations: true,
  sound_alerts: false,
  primary_font: "Segoe UI",
  preferred_chart_theme: "executive",
  landing_module: "dashboard",
};

const loadPlatformSettings = (): PlatformSettings => {
  const raw = localStorage.getItem(PLATFORM_SETTINGS_KEY);
  if (!raw) return defaultPlatformSettings;
  try {
    return { ...defaultPlatformSettings, ...(JSON.parse(raw) as PlatformSettings) };
  } catch {
    return defaultPlatformSettings;
  }
};

const applyFontPreference = (font: PlatformSettings["primary_font"]) => {
  if (font === "Inter") {
    document.body.style.fontFamily = "Inter, Segoe UI, sans-serif";
    return;
  }
  if (font === "IBM Plex Sans") {
    document.body.style.fontFamily = "IBM Plex Sans, Segoe UI, sans-serif";
    return;
  }
  document.body.style.fontFamily = "Segoe UI, Helvetica Neue, sans-serif";
};

export const AdminPortalPage = () => {
  const { user, activeTenantId, setActiveTenantId } = useAuth();
  const [activeTab, setActiveTab] = useState<TabId>(() => {
    const module = loadPlatformSettings().landing_module;
    if (module === "tenants" || module === "projects" || module === "analytics") {
      return module as TabId;
    }
    return "dashboard";
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [sites, setSites] = useState<Array<{ id: string; name: string; location: string }>>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [operators, setOperators] = useState<Operator[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [branding, setBranding] = useState<Branding | null>(null);
  const [users, setUsers] = useState<UserProfile[]>([]);

  const [tenantName, setTenantName] = useState("");
  const [tenantSlug, setTenantSlug] = useState("");
  const [tenantEmail, setTenantEmail] = useState("");

  const [siteName, setSiteName] = useState("");
  const [siteLocation, setSiteLocation] = useState("");
  const [projectSiteId, setProjectSiteId] = useState("");

  const [projectName, setProjectName] = useState("");
  const [projectClient, setProjectClient] = useState("");
  const [projectLocation, setProjectLocation] = useState("");
  const [projectStartDate, setProjectStartDate] = useState("");
  const [projectEndDate, setProjectEndDate] = useState("");

  const [operatorCode, setOperatorCode] = useState("");
  const [operatorName, setOperatorName] = useState("");

  const [toolCode, setToolCode] = useState("");
  const [toolModel, setToolModel] = useState("");
  const [toolCalibrationDate, setToolCalibrationDate] = useState("");

  const [woProjectId, setWoProjectId] = useState("");
  const [woCode, setWoCode] = useState("");
  const [woName, setWoName] = useState("");
  const [woFile, setWoFile] = useState<File | null>(null);
  const [woProgress, setWoProgress] = useState(0);

  const [reportType, setReportType] = useState<
    "Joint Certification Report" | "Work Order Report" | "Project Quality Report"
  >("Project Quality Report");
  const [reportProjectId, setReportProjectId] = useState("");
  const [reportWorkOrderId, setReportWorkOrderId] = useState("");
  const [reportJointId, setReportJointId] = useState("");

  const [brandingName, setBrandingName] = useState("");
  const [brandingPrimary, setBrandingPrimary] = useState("#0f766e");
  const [brandingSecondary, setBrandingSecondary] = useState("#1f2937");
  const [brandingLogoPath, setBrandingLogoPath] = useState("");
  const [logoPreviewUrl, setLogoPreviewUrl] = useState<string | null>(null);

  const [selectedTenantForBilling, setSelectedTenantForBilling] = useState("");
  const [selectedPlanName, setSelectedPlanName] = useState<"Basic" | "Professional" | "Enterprise">("Basic");
  const [selectedPlanStatus, setSelectedPlanStatus] = useState<"ACTIVE" | "PAUSED" | "CANCELLED">("ACTIVE");

  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserPassword, setNewUserPassword] = useState("");
  const [newUserRole, setNewUserRole] = useState<UserRole>("CLIENT_VIEWER");
  const [newUserTenantId, setNewUserTenantId] = useState("");

  const [platformSettings, setPlatformSettings] = useState<PlatformSettings>(() => loadPlatformSettings());

  const { isConnected, lastEvent } = useDashboardRealtime();

  const isAbsUser = ABS_ROLES.includes(user?.role || "CLIENT_VIEWER");

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        analyticsResult,
        executionRows,
        tenantRows,
        projectRows,
        siteRows,
        workOrderRows,
        operatorRows,
        toolRows,
        reportRows,
        notificationRows,
        auditRows,
        planRows,
        sub,
        brandingRow,
        userRows,
      ] = await Promise.all([
        analyticsApi.dashboard(),
        executionsApi.list(),
        tenantsApi.list(),
        projectsApi.list(),
        projectsApi.listSites(),
        workOrdersApi.list(),
        operatorsApi.list(),
        toolsApi.list(),
        reportsApi.list(),
        notificationsApi.list(),
        auditApi.list(),
        billingApi.plans(),
        billingApi.subscription(),
        brandingApi.get(),
        usersApi.list(),
      ]);

      setAnalytics(analyticsResult);
      setExecutions(executionRows);
      setTenants(tenantRows);
      setProjects(projectRows);
      setSites(siteRows);
      setWorkOrders(workOrderRows);
      setOperators(operatorRows);
      setTools(toolRows);
      setReports(reportRows);
      setNotifications(notificationRows);
      setAuditLogs(auditRows);
      setPlans(planRows);
      setSubscription(sub);
      setBranding(brandingRow);
      setUsers(userRows);

      if (!selectedTenantForBilling && tenantRows[0]) {
        setSelectedTenantForBilling(tenantRows[0].id);
      }
      if (!newUserTenantId && tenantRows[0]) {
        setNewUserTenantId(tenantRows[0].id);
      }
      if (planRows[0]) {
        setSelectedPlanName(planRows[0].name);
      }
      if (brandingRow) {
        setBrandingName(brandingRow.client_display_name);
        setBrandingPrimary(brandingRow.primary_color);
        setBrandingSecondary(brandingRow.secondary_color);
        setBrandingLogoPath(brandingRow.company_logo_path ?? "");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin center");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    applyFontPreference(platformSettings.primary_font);
  }, [platformSettings.primary_font]);

  useEffect(() => {
    void loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTenantId]);

  useEffect(() => {
    if (!platformSettings.realtime_auto_refresh) return;
    const interval = window.setInterval(() => {
      if (activeTab === "dashboard" || activeTab === "analytics") {
        void Promise.all([analyticsApi.dashboard(), executionsApi.list()]).then(([analyticsResult, executionRows]) => {
          setAnalytics(analyticsResult);
          setExecutions(executionRows);
        });
      }
    }, 20000);

    return () => window.clearInterval(interval);
  }, [activeTab, platformSettings.realtime_auto_refresh]);

  useEffect(() => {
    if (!lastEvent) return;
    void Promise.all([analyticsApi.dashboard(), executionsApi.list()]).then(([analyticsResult, executionRows]) => {
      setAnalytics(analyticsResult);
      setExecutions(executionRows);
    });
  }, [lastEvent]);

  const failedExecutions = useMemo(
    () => executions.filter((item) => item.status === "NOK" || item.status === "OutOfTolerance"),
    [executions],
  );

  const handleAction = async (action: () => Promise<void>, successMessage: string) => {
    try {
      setError(null);
      await action();
      setNotice(successMessage);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Operation failed");
    }
  };

  const handleLogoPick = (file: File) => {
    if (logoPreviewUrl) {
      URL.revokeObjectURL(logoPreviewUrl);
    }
    const next = URL.createObjectURL(file);
    setLogoPreviewUrl(next);
    setBrandingLogoPath((prev) => prev || file.name);
  };

  const headerActions = (
    <>
      {isAbsUser ? (
        <select
          className="field-input max-w-64"
          value={activeTenantId}
          onChange={(event) => setActiveTenantId(event.target.value)}
        >
          {tenants.map((tenant) => (
            <option key={tenant.id} value={tenant.id}>
              {tenant.name}
            </option>
          ))}
        </select>
      ) : null}
      <Button variant="secondary" onClick={() => void loadAll()}>
        Refresh Data
      </Button>
    </>
  );

  return (
    <PortalLayout
      title="ABS Admin Center"
      subtitle="Microsoft-style enterprise control center for platform governance"
      navItems={navItems.map((item) => ({ id: item.id, label: item.label }))}
      activeNav={activeTab}
      onSelectNav={(id) => setActiveTab(id as TabId)}
      headerActions={headerActions}
    >
      {loading ? <Loader label="Loading admin center..." /> : null}
      {error ? <div className="rounded-lg bg-rose-500/20 px-3 py-2 text-sm text-rose-200">{error}</div> : null}
      {notice ? <div className="rounded-lg bg-emerald-500/20 px-3 py-2 text-sm text-emerald-200">{notice}</div> : null}

      {activeTab === "dashboard" && analytics ? (
        <>
          <RealtimeBanner connected={isConnected} event={lastEvent} />
          <KpiGrid kpis={analytics.kpis} />
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <TorqueAngleScatter points={analytics.torque_vs_angle} />
            <TorqueDistributionChart data={analytics.torque_distribution} />
            <FailureTrendChart executions={executions} />
            <OperatorPerformanceChart data={analytics.operator_analytics} />
            <ToolUsageChart data={analytics.tool_health} />
            <div className="panel p-4">
              <h3 className="panel-title">Enterprise Status</h3>
              <p className="mt-3 text-sm text-textMuted">Failed execution rows across selected tenant:</p>
              <p className="mt-1 text-4xl font-bold text-accentAlt">{formatNumber(failedExecutions.length)}</p>
              <p className="mt-3 text-xs text-textMuted">Reports generated: {formatNumber(reports.length)}</p>
              <p className="text-xs text-textMuted">Users provisioned: {formatNumber(users.length)}</p>
            </div>
          </div>
        </>
      ) : null}

      {activeTab === "tenants" ? (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <div className="panel p-4">
            <h3 className="panel-title">Create Tenant (Customer)</h3>
            <div className="mt-3 space-y-3">
              <input className="field-input" placeholder="Tenant name" value={tenantName} onChange={(event) => setTenantName(event.target.value)} />
              <input className="field-input" placeholder="Tenant slug" value={tenantSlug} onChange={(event) => setTenantSlug(event.target.value)} />
              <input className="field-input" placeholder="Contact email" value={tenantEmail} onChange={(event) => setTenantEmail(event.target.value)} />
              <Button className="w-full" onClick={() => void handleAction(async () => {
                await tenantsApi.create({ name: tenantName, slug: tenantSlug, contact_email: tenantEmail });
                setTenantName("");
                setTenantSlug("");
                setTenantEmail("");
              }, "Tenant created")}>Create Tenant</Button>
            </div>
          </div>
          <div className="xl:col-span-2">
            <DataTable
              columns={[
                { key: "name", label: "Tenant", render: (row) => row.name },
                { key: "slug", label: "Slug", render: (row) => row.slug },
                { key: "email", label: "Contact", render: (row) => row.contact_email },
                { key: "created", label: "Created", render: (row) => formatDateTime(row.created_at) },
                { key: "status", label: "Status", render: (row) => <Badge tone={row.is_active ? "success" : "warning"}>{row.is_active ? "Active" : "Inactive"}</Badge> },
              ]}
              rows={tenants}
              rowKey={(row) => row.id}
            />
          </div>
        </div>
      ) : null}

      {activeTab === "projects" ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <div className="panel p-4">
              <h3 className="panel-title">Create Site</h3>
              <div className="mt-3 space-y-3">
                <input className="field-input" placeholder="Site name" value={siteName} onChange={(event) => setSiteName(event.target.value)} />
                <input className="field-input" placeholder="Location" value={siteLocation} onChange={(event) => setSiteLocation(event.target.value)} />
                <Button className="w-full" onClick={() => void handleAction(async () => {
                  await projectsApi.createSite({ name: siteName, location: siteLocation });
                  setSiteName("");
                  setSiteLocation("");
                }, "Site created")}>Create Site</Button>
              </div>
            </div>
            <div className="panel p-4">
              <h3 className="panel-title">Create Project</h3>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <input className="field-input" placeholder="Project name" value={projectName} onChange={(event) => setProjectName(event.target.value)} />
                <input className="field-input" placeholder="Client name" value={projectClient} onChange={(event) => setProjectClient(event.target.value)} />
                <input className="field-input" placeholder="Location" value={projectLocation} onChange={(event) => setProjectLocation(event.target.value)} />
                <select className="field-input" value={projectSiteId} onChange={(event) => setProjectSiteId(event.target.value)}>
                  <option value="">Site (optional)</option>
                  {sites.map((site) => (
                    <option key={site.id} value={site.id}>{site.name}</option>
                  ))}
                </select>
                <input className="field-input" type="date" value={projectStartDate} onChange={(event) => setProjectStartDate(event.target.value)} />
                <input className="field-input" type="date" value={projectEndDate} onChange={(event) => setProjectEndDate(event.target.value)} />
                <Button className="sm:col-span-2" onClick={() => void handleAction(async () => {
                  await projectsApi.create({
                    name: projectName,
                    client_name: projectClient,
                    location: projectLocation,
                    start_date: projectStartDate,
                    expected_completion: projectEndDate,
                    site_id: projectSiteId || null,
                  });
                  setProjectName("");
                  setProjectClient("");
                  setProjectLocation("");
                  setProjectSiteId("");
                  setProjectStartDate("");
                  setProjectEndDate("");
                }, "Project created")}>Create Project</Button>
              </div>
            </div>
          </div>
          <DataTable
            columns={[
              { key: "name", label: "Project", render: (row) => row.name },
              { key: "client", label: "Client", render: (row) => row.client_name },
              { key: "site", label: "Site", render: (row) => row.site_id ?? "-" },
              { key: "location", label: "Location", render: (row) => row.location },
              { key: "start", label: "Start", render: (row) => formatDate(row.start_date) },
              { key: "end", label: "Expected Completion", render: (row) => formatDate(row.expected_completion) },
            ]}
            rows={projects}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "workOrders" ? (
        <div className="space-y-4">
          <div className="panel p-4">
            <h3 className="panel-title">Work Order Upload Center</h3>
            <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-4">
              <select className="field-input" value={woProjectId} onChange={(event) => setWoProjectId(event.target.value)}>
                <option value="">Select project</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>{project.name}</option>
                ))}
              </select>
              <input className="field-input" placeholder="WO code" value={woCode} onChange={(event) => setWoCode(event.target.value)} />
              <input className="field-input" placeholder="WO name" value={woName} onChange={(event) => setWoName(event.target.value)} />
              <div className="flex items-center">
                <Button className="w-full" onClick={() => void handleAction(async () => {
                  if (!woProjectId || !woCode || !woName || !woFile) throw new Error("Project, code, name and excel file are required");
                  setWoProgress(0);
                  await workOrdersApi.upload({ projectId: woProjectId, code: woCode, name: woName, file: woFile }, setWoProgress);
                  setWoProjectId("");
                  setWoCode("");
                  setWoName("");
                  setWoFile(null);
                  setWoProgress(0);
                }, "Work order uploaded")}>Process Work Order</Button>
              </div>
            </div>
            <div className="mt-4">
              <FileDropzone onFileChange={setWoFile} />
            </div>
            {woProgress > 0 ? <p className="mt-2 text-xs text-textMuted">Upload progress: {woProgress}%</p> : null}
          </div>
          <DataTable
            columns={[
              { key: "code", label: "Code", render: (row) => row.code },
              { key: "name", label: "Name", render: (row) => row.name },
              { key: "project", label: "Project", render: (row) => row.project_id },
              { key: "source", label: "Source", render: (row) => row.source_filename },
            ]}
            rows={workOrders}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "operators" ? (
        <div className="space-y-4">
          <div className="panel p-4">
            <h3 className="panel-title">Operator Registry</h3>
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <input className="field-input" placeholder="Operator code" value={operatorCode} onChange={(event) => setOperatorCode(event.target.value)} />
              <input className="field-input" placeholder="Operator name" value={operatorName} onChange={(event) => setOperatorName(event.target.value)} />
              <Button onClick={() => void handleAction(async () => {
                await operatorsApi.create({ operator_code: operatorCode, name: operatorName });
                setOperatorCode("");
                setOperatorName("");
              }, "Operator created")}>Add Operator</Button>
            </div>
          </div>
          <DataTable
            columns={[
              { key: "code", label: "Code", render: (row) => row.operator_code },
              { key: "name", label: "Name", render: (row) => row.name },
              { key: "jobs", label: "Jobs Completed", render: (row) => formatNumber(row.jobs_completed) },
              { key: "error", label: "Error Rate", render: (row) => `${row.error_rate.toFixed(2)}%` },
              { key: "deviation", label: "Avg Torque Deviation", render: (row) => row.avg_torque_deviation.toFixed(2) },
            ]}
            rows={operators}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "tools" ? (
        <div className="space-y-4">
          <div className="panel p-4">
            <h3 className="panel-title">Tool Registry</h3>
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-4">
              <input className="field-input" placeholder="Tool code" value={toolCode} onChange={(event) => setToolCode(event.target.value)} />
              <input className="field-input" placeholder="Model" value={toolModel} onChange={(event) => setToolModel(event.target.value)} />
              <input className="field-input" type="date" value={toolCalibrationDate} onChange={(event) => setToolCalibrationDate(event.target.value)} />
              <Button onClick={() => void handleAction(async () => {
                await toolsApi.create({ tool_code: toolCode, model: toolModel, calibration_date: toolCalibrationDate || null });
                setToolCode("");
                setToolModel("");
                setToolCalibrationDate("");
              }, "Tool created")}>Add Tool</Button>
            </div>
          </div>
          <DataTable
            columns={[
              { key: "code", label: "Tool", render: (row) => row.tool_code },
              { key: "model", label: "Model", render: (row) => row.model },
              { key: "cycles", label: "Cycles", render: (row) => formatNumber(row.total_cycles) },
              { key: "health", label: "Health", render: (row) => row.health_status },
              { key: "calibration", label: "Calibration", render: (row) => formatDate(row.calibration_date) },
            ]}
            rows={tools}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "analytics" && analytics ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <TorqueAngleScatter points={analytics.torque_vs_angle} />
            <TorqueDistributionChart data={analytics.torque_distribution} />
            <FailureTrendChart executions={executions} />
            <OperatorPerformanceChart data={analytics.operator_analytics} />
            <ToolUsageChart data={analytics.tool_health} />
          </div>
          <JointHeatmap rows={analytics.compliance_heatmap} />
          <DataTable
            columns={[
              { key: "joint", label: "Joint", render: (row) => row.joint_id },
              { key: "bolt", label: "Bolt", render: (row) => String(row.bolt_no) },
              { key: "status", label: "Status", render: (row) => row.status },
              { key: "source", label: "Source File", render: (row) => row.source_file },
            ]}
            rows={failedExecutions}
            rowKey={(row) => row.id}
            emptyLabel="No failed bolts detected."
          />
        </div>
      ) : null}

      {activeTab === "reports" ? (
        <div className="space-y-4">
          <div className="panel p-4">
            <h3 className="panel-title">Generate Report</h3>
            <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-5">
              <select className="field-input" value={reportType} onChange={(event) => setReportType(event.target.value as typeof reportType)}>
                <option value="Joint Certification Report">Joint Certification Report</option>
                <option value="Work Order Report">Work Order Report</option>
                <option value="Project Quality Report">Project Quality Report</option>
              </select>
              <select className="field-input" value={reportProjectId} onChange={(event) => setReportProjectId(event.target.value)}>
                <option value="">Project (optional)</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>{project.name}</option>
                ))}
              </select>
              <select className="field-input" value={reportWorkOrderId} onChange={(event) => setReportWorkOrderId(event.target.value)}>
                <option value="">Work Order (optional)</option>
                {workOrders.map((workOrder) => (
                  <option key={workOrder.id} value={workOrder.id}>{workOrder.code}</option>
                ))}
              </select>
              <input className="field-input" placeholder="Joint UUID" value={reportJointId} onChange={(event) => setReportJointId(event.target.value)} />
              <Button onClick={() => void handleAction(async () => {
                await reportsApi.create({
                  report_type: reportType,
                  project_id: reportProjectId || undefined,
                  work_order_id: reportWorkOrderId || undefined,
                  joint_id: reportJointId || undefined,
                });
                setReportJointId("");
              }, "Report generated")}>Generate</Button>
            </div>
          </div>
          <DataTable
            columns={[
              { key: "type", label: "Type", render: (row) => row.report_type },
              { key: "project", label: "Project", render: (row) => row.project_id ?? "-" },
              { key: "wo", label: "Work Order", render: (row) => row.work_order_id ?? "-" },
              {
                key: "download",
                label: "Download",
                render: (row) => (
                  <a className="text-accent underline" href={reportsApi.downloadUrl(row.id)} target="_blank" rel="noreferrer">
                    Download PDF
                  </a>
                ),
              },
            ]}
            rows={reports}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "users" ? (
        <div className="space-y-4">
          <div className="panel p-4">
            <h3 className="panel-title">User & Role Management</h3>
            <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-5">
              <input className="field-input" placeholder="Full name" value={newUserName} onChange={(event) => setNewUserName(event.target.value)} />
              <input className="field-input" placeholder="Email" value={newUserEmail} onChange={(event) => setNewUserEmail(event.target.value)} />
              <input className="field-input" type="password" placeholder="Password" value={newUserPassword} onChange={(event) => setNewUserPassword(event.target.value)} />
              <select className="field-input" value={newUserRole} onChange={(event) => setNewUserRole(event.target.value as UserRole)}>
                <option value="SUPER_ADMIN">SUPER_ADMIN</option>
                <option value="ABS_ENGINEER">ABS_ENGINEER</option>
                <option value="CLIENT_ADMIN">CLIENT_ADMIN</option>
                <option value="CLIENT_ENGINEER">CLIENT_ENGINEER</option>
                <option value="CLIENT_VIEWER">CLIENT_VIEWER</option>
              </select>
              <select className="field-input" value={newUserTenantId} onChange={(event) => setNewUserTenantId(event.target.value)}>
                <option value="">Tenant</option>
                {tenants.map((tenant) => (
                  <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
                ))}
              </select>
            </div>
            <Button className="mt-3" onClick={() => void handleAction(async () => {
              await authApi.createUser({
                full_name: newUserName,
                email: newUserEmail,
                password: newUserPassword,
                role: newUserRole,
                tenant_id: newUserTenantId || null,
              });
              setNewUserName("");
              setNewUserEmail("");
              setNewUserPassword("");
              setNewUserRole("CLIENT_VIEWER");
            }, "User created")}>Create User</Button>
          </div>

          <DataTable
            columns={[
              { key: "name", label: "Name", render: (row) => row.full_name },
              { key: "email", label: "Email", render: (row) => row.email },
              { key: "role", label: "Role", render: (row) => row.role },
              { key: "tenant", label: "Tenant", render: (row) => row.tenant_id },
              { key: "status", label: "Active", render: (row) => <Badge tone={row.is_active ? "success" : "warning"}>{row.is_active ? "Yes" : "No"}</Badge> },
            ]}
            rows={users}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "billing" ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <div className="panel p-4">
              <h3 className="panel-title">Subscription Control</h3>
              <div className="mt-3 space-y-3">
                <select className="field-input" value={selectedTenantForBilling} onChange={(event) => setSelectedTenantForBilling(event.target.value)}>
                  <option value="">Select tenant</option>
                  {tenants.map((tenant) => (
                    <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
                  ))}
                </select>
                <select className="field-input" value={selectedPlanName} onChange={(event) => setSelectedPlanName(event.target.value as typeof selectedPlanName)}>
                  <option value="Basic">Basic</option>
                  <option value="Professional">Professional</option>
                  <option value="Enterprise">Enterprise</option>
                </select>
                <select className="field-input" value={selectedPlanStatus} onChange={(event) => setSelectedPlanStatus(event.target.value as typeof selectedPlanStatus)}>
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="PAUSED">PAUSED</option>
                  <option value="CANCELLED">CANCELLED</option>
                </select>
                <Button onClick={() => void handleAction(async () => {
                  if (!selectedTenantForBilling) throw new Error("Select a tenant first");
                  await billingApi.updateSubscription({
                    tenant_id: selectedTenantForBilling,
                    plan_name: selectedPlanName,
                    status: selectedPlanStatus,
                  });
                }, "Subscription updated")}>Apply Subscription</Button>
              </div>
            </div>
            <div className="panel p-4">
              <h3 className="panel-title">Current Subscription</h3>
              {subscription ? (
                <div className="mt-3 rounded-lg border border-border bg-panelSoft p-3 text-sm text-textMuted">
                  <p>Status: {subscription.status}</p>
                  <p>Seats used: {subscription.seats_used}</p>
                  <p>Usage this month: {subscription.current_month_usage}</p>
                  <p>Tenant: {subscription.tenant_id}</p>
                </div>
              ) : (
                <p className="mt-3 text-sm text-textMuted">No subscription loaded.</p>
              )}
            </div>
          </div>

          <DataTable
            columns={[
              { key: "name", label: "Plan", render: (row) => row.name },
              { key: "price", label: "Monthly Price", render: (row) => `$${row.monthly_price}` },
              { key: "seat", label: "Seat Limit", render: (row) => String(row.seat_limit) },
              { key: "usage", label: "Usage Limit", render: (row) => String(row.usage_limit) },
            ]}
            rows={plans}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "audit" ? (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          <DataTable
            columns={[
              { key: "event", label: "Event", render: (row) => row.event_type },
              { key: "resource", label: "Resource", render: (row) => row.resource_type },
              { key: "description", label: "Description", render: (row) => row.description },
              { key: "time", label: "Time", render: (row) => formatDateTime(row.created_at) },
            ]}
            rows={auditLogs}
            rowKey={(row) => row.id}
          />
          <DataTable
            columns={[
              { key: "severity", label: "Severity", render: (row) => row.severity },
              { key: "title", label: "Title", render: (row) => row.title },
              { key: "message", label: "Message", render: (row) => row.message },
              {
                key: "mark",
                label: "Action",
                render: (row) => (
                  <Button
                    variant="secondary"
                    onClick={() =>
                      void handleAction(async () => {
                        await notificationsApi.markRead(row.id, !row.is_read);
                      }, "Notification updated")
                    }
                  >
                    {row.is_read ? "Mark Unread" : "Mark Read"}
                  </Button>
                ),
              },
            ]}
            rows={notifications}
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {activeTab === "platformSettings" ? (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          <div className="panel p-4">
            <h3 className="panel-title">Platform Configuration</h3>
            <div className="mt-3 space-y-3">
              <ToggleSwitch
                enabled={platformSettings.compact_navigation}
                onChange={(next) => setPlatformSettings((prev) => ({ ...prev, compact_navigation: next }))}
                label="Compact navigation"
                description="Use denser sidebar spacing for high-information operators."
              />
              <ToggleSwitch
                enabled={platformSettings.realtime_auto_refresh}
                onChange={(next) => setPlatformSettings((prev) => ({ ...prev, realtime_auto_refresh: next }))}
                label="Realtime auto refresh"
                description="Automatically refresh dashboards every 20 seconds."
              />
              <ToggleSwitch
                enabled={platformSettings.dashboard_animations}
                onChange={(next) => setPlatformSettings((prev) => ({ ...prev, dashboard_animations: next }))}
                label="Dashboard animations"
                description="Enable chart transition effects."
              />
              <ToggleSwitch
                enabled={platformSettings.sound_alerts}
                onChange={(next) => setPlatformSettings((prev) => ({ ...prev, sound_alerts: next }))}
                label="Sound alerts"
                description="Play audio cues for critical warnings."
              />
            </div>
          </div>

          <div className="panel p-4">
            <h3 className="panel-title">Portal Customization</h3>
            <div className="mt-3 space-y-3">
              <select className="field-input" value={platformSettings.primary_font} onChange={(event) => setPlatformSettings((prev) => ({ ...prev, primary_font: event.target.value as PlatformSettings["primary_font"] }))}>
                <option value="Segoe UI">Segoe UI</option>
                <option value="Inter">Inter</option>
                <option value="IBM Plex Sans">IBM Plex Sans</option>
              </select>
              <select className="field-input" value={platformSettings.preferred_chart_theme} onChange={(event) => setPlatformSettings((prev) => ({ ...prev, preferred_chart_theme: event.target.value as PlatformSettings["preferred_chart_theme"] }))}>
                <option value="executive">Executive</option>
                <option value="classic">Classic</option>
                <option value="contrast">High Contrast</option>
              </select>
              <select className="field-input" value={platformSettings.landing_module} onChange={(event) => setPlatformSettings((prev) => ({ ...prev, landing_module: event.target.value as PlatformSettings["landing_module"] }))}>
                <option value="dashboard">Dashboard</option>
                <option value="tenants">Tenants</option>
                <option value="projects">Projects</option>
                <option value="analytics">Analytics</option>
              </select>
              <Button onClick={() => {
                localStorage.setItem(PLATFORM_SETTINGS_KEY, JSON.stringify(platformSettings));
                applyFontPreference(platformSettings.primary_font);
                setNotice("Platform settings saved");
              }}>
                Save Platform Settings
              </Button>
              <p className="text-xs text-textMuted">
                These settings are GUI-driven client preferences. Persisting globally to backend would require a dedicated settings API.
              </p>
            </div>
          </div>
        </div>
      ) : null}

      {activeTab === "branding" ? (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          <div className="space-y-4">
            <LogoPicker
              previewUrl={logoPreviewUrl || brandingLogoPath || null}
              onPick={handleLogoPick}
              onClear={() => {
                if (logoPreviewUrl) URL.revokeObjectURL(logoPreviewUrl);
                setLogoPreviewUrl(null);
              }}
            />
            <div className="panel p-4">
              <h3 className="panel-title">Branding Studio</h3>
              <div className="mt-3 space-y-3">
                <input className="field-input" placeholder="Display name" value={brandingName} onChange={(event) => setBrandingName(event.target.value)} />
                <div className="grid grid-cols-2 gap-3">
                  <input className="field-input" type="color" value={brandingPrimary} onChange={(event) => setBrandingPrimary(event.target.value)} />
                  <input className="field-input" type="color" value={brandingSecondary} onChange={(event) => setBrandingSecondary(event.target.value)} />
                </div>
                <input className="field-input" placeholder="Logo URL/Path" value={brandingLogoPath} onChange={(event) => setBrandingLogoPath(event.target.value)} />
                <Button onClick={() => void handleAction(async () => {
                  await brandingApi.update({
                    client_display_name: brandingName,
                    primary_color: brandingPrimary,
                    secondary_color: brandingSecondary,
                    company_logo_path: brandingLogoPath || null,
                  });
                }, "Branding settings updated")}>Save Branding</Button>
              </div>
            </div>
          </div>

          <div className="panel p-4">
            <h3 className="panel-title">Live Brand Preview</h3>
            <div className="mt-4 rounded-xl border border-border p-4" style={{ background: `linear-gradient(135deg, ${brandingPrimary}, ${brandingSecondary})` }}>
              <div className="rounded-lg bg-black/20 p-4 text-white">
                <p className="text-xs uppercase tracking-widest">Portal Preview</p>
                <h4 className="mt-2 text-2xl font-bold">{brandingName || "ABS Enterprise Portal"}</h4>
                <p className="mt-2 text-sm text-white/80">Tenant-aware industrial tightening intelligence workspace.</p>
                {logoPreviewUrl || brandingLogoPath ? (
                  <div className="mt-4 rounded bg-white/20 p-3">
                    <img src={logoPreviewUrl || brandingLogoPath} alt="Brand logo" className="max-h-14 max-w-48 object-contain" />
                  </div>
                ) : null}
              </div>
            </div>
            {branding ? <p className="mt-3 text-xs text-textMuted">Current branding tenant: {branding.tenant_id}</p> : null}
          </div>
        </div>
      ) : null}
    </PortalLayout>
  );
};


