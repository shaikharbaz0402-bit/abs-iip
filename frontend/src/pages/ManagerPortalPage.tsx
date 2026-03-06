import { useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/data/DataTable";
import { Button } from "@/components/ui/Button";
import { Loader } from "@/components/ui/Loader";
import { KpiGrid } from "@/dashboards/KpiGrid";
import { FailureTrendChart } from "@/dashboards/FailureTrendChart";
import { OperatorPerformanceChart } from "@/dashboards/OperatorPerformanceChart";
import { RealtimeBanner } from "@/dashboards/RealtimeBanner";
import { ToolUsageChart } from "@/dashboards/ToolUsageChart";
import { PortalLayout } from "@/layouts/PortalLayout";
import { useDashboardRealtime } from "@/hooks/useDashboardRealtime";
import { analyticsApi, executionsApi, projectsApi, reportsApi, workOrdersApi } from "@/services/absApi";
import type { DashboardAnalytics, Execution, Project, Report, WorkOrder } from "@/types/domain";
import { formatDate, formatNumber } from "@/utils/format";

const navItems = [
  { id: "overview", label: "Project Dashboard" },
  { id: "workorders", label: "Work Orders" },
  { id: "reports", label: "Reports" },
];

type TabId = (typeof navItems)[number]["id"];

export const ManagerPortalPage = () => {
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedProject, setSelectedProject] = useState("");

  const { isConnected, lastEvent } = useDashboardRealtime();

  const loadData = async (projectId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const [analyticsResult, projectRows, workOrderRows, executionRows, reportRows] = await Promise.all([
        analyticsApi.dashboard(projectId),
        projectsApi.list(),
        workOrdersApi.list(projectId),
        executionsApi.list(projectId ? { projectId } : undefined),
        reportsApi.list(),
      ]);

      setAnalytics(analyticsResult);
      setProjects(projectRows);
      setWorkOrders(workOrderRows);
      setExecutions(executionRows);
      setReports(reportRows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load manager portal");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  useEffect(() => {
    if (!lastEvent) return;
    void loadData(selectedProject || undefined);
  }, [lastEvent, selectedProject]);

  const failedExecutions = useMemo(
    () => executions.filter((execution) => execution.status === "NOK" || execution.status === "OutOfTolerance"),
    [executions],
  );

  const managerReports = useMemo(() => reports.filter((report) => report.report_type !== "Joint Certification Report"), [reports]);

  return (
    <PortalLayout
      title="Project Manager Portal"
      subtitle="Progress tracking, execution health, and delivery reporting"
      navItems={navItems}
      activeNav={activeTab}
      onSelectNav={(id) => setActiveTab(id as TabId)}
    >
      {loading ? <Loader label="Loading manager data..." /> : null}
      {error ? <div className="rounded-lg bg-rose-500/20 px-3 py-2 text-sm text-rose-200">{error}</div> : null}

      <div className="panel flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-semibold text-text">Project Scope</p>
          <p className="text-xs text-textMuted">Filter dashboards to one project or keep all projects combined.</p>
        </div>
        <div className="flex w-full gap-3 lg:w-auto">
          <select
            className="field-input"
            value={selectedProject}
            onChange={(event) => {
              const next = event.target.value;
              setSelectedProject(next);
              void loadData(next || undefined);
            }}
          >
            <option value="">All Projects</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
          <Button variant="secondary" onClick={() => void loadData(selectedProject || undefined)}>
            Refresh
          </Button>
        </div>
      </div>

      {activeTab === "overview" && analytics ? (
        <>
          <RealtimeBanner connected={isConnected} event={lastEvent} />
          <KpiGrid kpis={analytics.kpis} />

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
            <div className="panel p-4">
              <p className="text-sm text-textMuted">Active Work Orders</p>
              <p className="mt-2 text-3xl font-bold text-text">{formatNumber(workOrders.length)}</p>
            </div>
            <div className="panel p-4">
              <p className="text-sm text-textMuted">Failed Executions</p>
              <p className="mt-2 text-3xl font-bold text-accentAlt">{formatNumber(failedExecutions.length)}</p>
            </div>
            <div className="panel p-4">
              <p className="text-sm text-textMuted">Report Artifacts</p>
              <p className="mt-2 text-3xl font-bold text-text">{formatNumber(managerReports.length)}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <FailureTrendChart executions={executions} />
            <ToolUsageChart data={analytics.tool_health} />
            <OperatorPerformanceChart data={analytics.operator_analytics} />
            <div className="panel p-4">
              <h3 className="panel-title">Project List</h3>
              <div className="mt-3 space-y-2 text-sm text-textMuted">
                {projects.map((project) => (
                  <div key={project.id} className="rounded-lg border border-border bg-panelSoft px-3 py-2">
                    <p className="font-semibold text-text">{project.name}</p>
                    <p>
                      {project.client_name} | {project.location}
                    </p>
                    <p>
                      {formatDate(project.start_date)} - {formatDate(project.expected_completion)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      ) : null}

      {activeTab === "workorders" ? (
        <>
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

          <DataTable
            columns={[
              { key: "joint", label: "Joint", render: (row) => row.joint_id },
              { key: "bolt", label: "Bolt", render: (row) => row.bolt_no.toString() },
              { key: "status", label: "Status", render: (row) => row.status },
              { key: "source", label: "Source File", render: (row) => row.source_file },
            ]}
            rows={failedExecutions}
            rowKey={(row) => row.id}
            emptyLabel="No failed executions found for the selected scope."
          />
        </>
      ) : null}

      {activeTab === "reports" ? (
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
                  PDF
                </a>
              ),
            },
          ]}
          rows={managerReports}
          rowKey={(row) => row.id}
        />
      ) : null}
    </PortalLayout>
  );
};
