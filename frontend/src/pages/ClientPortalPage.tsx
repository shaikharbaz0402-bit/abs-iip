import { useEffect, useState } from "react";

import { DataTable } from "@/components/data/DataTable";
import { Button } from "@/components/ui/Button";
import { Loader } from "@/components/ui/Loader";
import { KpiGrid } from "@/dashboards/KpiGrid";
import { RealtimeBanner } from "@/dashboards/RealtimeBanner";
import { ToolUsageChart } from "@/dashboards/ToolUsageChart";
import { OperatorPerformanceChart } from "@/dashboards/OperatorPerformanceChart";
import { PortalLayout } from "@/layouts/PortalLayout";
import { useDashboardRealtime } from "@/hooks/useDashboardRealtime";
import { analyticsApi, dashboardApi, projectsApi, reportsApi } from "@/services/absApi";
import type { ClientProgress, DashboardAnalytics, Project, Report } from "@/types/domain";
import { formatDate } from "@/utils/format";

const navItems = [
  { id: "overview", label: "Project Progress" },
  { id: "reports", label: "Reports" },
];

type TabId = (typeof navItems)[number]["id"];

export const ClientPortalPage = () => {
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedProject, setSelectedProject] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [clientProgress, setClientProgress] = useState<ClientProgress | null>(null);
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [reports, setReports] = useState<Report[]>([]);

  const { isConnected, lastEvent } = useDashboardRealtime();

  const loadData = async (projectId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const [projectRows, progressRows, analyticsRows, reportRows] = await Promise.all([
        projectsApi.list(),
        dashboardApi.clientProgress(projectId),
        analyticsApi.dashboard(projectId),
        reportsApi.list(),
      ]);

      setProjects(projectRows);
      setClientProgress(progressRows);
      setAnalytics(analyticsRows);
      setReports(reportRows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load client portal");
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

  return (
    <PortalLayout
      title="Client Portal"
      subtitle="Read-only access to delivery progress, quality metrics, and reports"
      navItems={navItems}
      activeNav={activeTab}
      onSelectNav={(id) => setActiveTab(id as TabId)}
    >
      {loading ? <Loader label="Loading client portal..." /> : null}
      {error ? <div className="rounded-lg bg-rose-500/20 px-3 py-2 text-sm text-rose-200">{error}</div> : null}

      <div className="panel flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-semibold text-text">Project Filter</p>
          <p className="text-xs text-textMuted">Choose one project for focused progress metrics.</p>
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

      {activeTab === "overview" ? (
        <>
          <RealtimeBanner connected={isConnected} event={lastEvent} />

          {analytics ? <KpiGrid kpis={analytics.kpis} /> : null}

          {clientProgress ? (
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
              <div className="panel p-4">
                <p className="text-sm text-textMuted">Total Joints</p>
                <p className="mt-2 text-3xl font-bold text-text">{clientProgress.total_joints}</p>
              </div>
              <div className="panel p-4">
                <p className="text-sm text-textMuted">Certified Joints</p>
                <p className="mt-2 text-3xl font-bold text-text">{clientProgress.certified_joints}</p>
              </div>
              <div className="panel p-4">
                <p className="text-sm text-textMuted">Completion</p>
                <p className="mt-2 text-3xl font-bold text-text">{clientProgress.completion_percentage.toFixed(2)}%</p>
              </div>
            </div>
          ) : null}

          {analytics ? (
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
              <ToolUsageChart data={analytics.tool_health} />
              <OperatorPerformanceChart data={analytics.operator_analytics} />
            </div>
          ) : null}

          {clientProgress ? (
            <DataTable
              columns={[
                { key: "joint", label: "Joint", render: (row) => row.joint_id },
                { key: "status", label: "Status", render: (row) => row.status },
                { key: "project", label: "Project", render: (row) => row.project_id },
              ]}
              rows={clientProgress.items}
              rowKey={(row, idx) => `${row.joint_id}-${idx}`}
            />
          ) : null}

          <DataTable
            columns={[
              { key: "name", label: "Project", render: (row) => row.name },
              { key: "client", label: "Client", render: (row) => row.client_name },
              { key: "location", label: "Location", render: (row) => row.location },
              { key: "start", label: "Start", render: (row) => formatDate(row.start_date) },
              { key: "end", label: "Expected Completion", render: (row) => formatDate(row.expected_completion) },
            ]}
            rows={projects}
            rowKey={(row) => row.id}
          />
        </>
      ) : null}

      {activeTab === "reports" ? (
        <DataTable
          columns={[
            { key: "type", label: "Type", render: (row) => row.report_type },
            { key: "project", label: "Project", render: (row) => row.project_id ?? "-" },
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
          rows={reports}
          rowKey={(row) => row.id}
        />
      ) : null}
    </PortalLayout>
  );
};
