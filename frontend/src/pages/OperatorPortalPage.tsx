import { useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/data/DataTable";
import { FileDropzone } from "@/components/forms/FileDropzone";
import { Button } from "@/components/ui/Button";
import { Loader } from "@/components/ui/Loader";
import { KpiGrid } from "@/dashboards/KpiGrid";
import { RealtimeBanner } from "@/dashboards/RealtimeBanner";
import { PortalLayout } from "@/layouts/PortalLayout";
import { useDashboardRealtime } from "@/hooks/useDashboardRealtime";
import { analyticsApi, executionsApi, reportsApi, workOrdersApi } from "@/services/absApi";
import type { DashboardAnalytics, Execution, Report, WorkOrder } from "@/types/domain";
import { formatNumber } from "@/utils/format";

const navItems = [
  { id: "upload", label: "Execution Upload" },
  { id: "monitor", label: "Execution Monitor" },
  { id: "reports", label: "Reports" },
];

type TabId = (typeof navItems)[number]["id"];

export const OperatorPortalPage = () => {
  const [activeTab, setActiveTab] = useState<TabId>("upload");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [reports, setReports] = useState<Report[]>([]);

  const [selectedWorkOrderId, setSelectedWorkOrderId] = useState("");
  const [executionFile, setExecutionFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { isConnected, lastEvent } = useDashboardRealtime();

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [analyticsResult, workOrderRows, executionRows, reportRows] = await Promise.all([
        analyticsApi.dashboard(),
        workOrdersApi.list(),
        executionsApi.list(),
        reportsApi.list(),
      ]);
      setAnalytics(analyticsResult);
      setWorkOrders(workOrderRows);
      setExecutions(executionRows);
      setReports(reportRows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load operator portal");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  useEffect(() => {
    if (!lastEvent) return;
    void loadData();
  }, [lastEvent]);

  const failedRows = useMemo(
    () => executions.filter((row) => row.status === "NOK" || row.status === "OutOfTolerance"),
    [executions],
  );

  const handleExecutionUpload = async () => {
    if (!executionFile) {
      setError("Please select a valid AGS Excel file.");
      return;
    }

    try {
      setUploadProgress(0);
      const result = await executionsApi.upload(
        {
          file: executionFile,
          workOrderId: selectedWorkOrderId || undefined,
        },
        setUploadProgress,
      );

      setNotice(
        `Execution synced for joint ${result.joint_id}. Status: ${result.updated_joint_status}. OK ${result.ok_bolts}, NOK ${result.nok_bolts}, Missing ${result.missing_bolts}`,
      );
      setExecutionFile(null);
      setUploadProgress(0);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Execution upload failed");
    }
  };

  return (
    <PortalLayout
      title="Operator Portal"
      subtitle="Upload AGS tightening reports and monitor execution quality"
      navItems={navItems}
      activeNav={activeTab}
      onSelectNav={(id) => setActiveTab(id as TabId)}
    >
      {loading ? <Loader label="Loading operator data..." /> : null}
      {error ? <div className="rounded-lg bg-rose-500/20 px-3 py-2 text-sm text-rose-200">{error}</div> : null}
      {notice ? <div className="rounded-lg bg-emerald-500/20 px-3 py-2 text-sm text-emerald-200">{notice}</div> : null}

      {activeTab === "upload" ? (
        <>
          <RealtimeBanner connected={isConnected} event={lastEvent} />
          {analytics ? <KpiGrid kpis={analytics.kpis} /> : null}

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-[2fr_1fr]">
            <div className="panel p-4">
              <h3 className="panel-title">Upload AGS Execution Report</h3>
              <p className="mt-1 text-sm text-textMuted">Drag and drop `.xls` or `.xlsx` file exported from AGS software.</p>

              <div className="mt-4 space-y-3">
                <select
                  className="field-input"
                  value={selectedWorkOrderId}
                  onChange={(event) => setSelectedWorkOrderId(event.target.value)}
                >
                  <option value="">Auto-match by VIN</option>
                  {workOrders.map((workOrder) => (
                    <option key={workOrder.id} value={workOrder.id}>
                      {workOrder.code} - {workOrder.name}
                    </option>
                  ))}
                </select>

                <FileDropzone onFileChange={setExecutionFile} />

                {uploadProgress > 0 ? (
                  <div className="rounded-lg bg-panelSoft p-3 text-sm text-textMuted">Upload progress: {uploadProgress}%</div>
                ) : null}

                <Button className="w-full" onClick={() => void handleExecutionUpload()}>
                  Process Execution Data
                </Button>
              </div>
            </div>

            <div className="panel p-4">
              <h3 className="panel-title">Quick Stats</h3>
              <div className="mt-4 space-y-2 text-sm text-textMuted">
                <div className="rounded-lg border border-border bg-panelSoft p-3">
                  <p>Total Work Orders</p>
                  <p className="mt-1 text-2xl font-bold text-text">{formatNumber(workOrders.length)}</p>
                </div>
                <div className="rounded-lg border border-border bg-panelSoft p-3">
                  <p>Total Executions</p>
                  <p className="mt-1 text-2xl font-bold text-text">{formatNumber(executions.length)}</p>
                </div>
                <div className="rounded-lg border border-border bg-panelSoft p-3">
                  <p>Failed Bolts</p>
                  <p className="mt-1 text-2xl font-bold text-accentAlt">{formatNumber(failedRows.length)}</p>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : null}

      {activeTab === "monitor" ? (
        <>
          <DataTable
            columns={[
              { key: "joint", label: "Joint", render: (row) => row.joint_id },
              { key: "bolt", label: "Bolt", render: (row) => row.bolt_no.toString() },
              { key: "status", label: "Status", render: (row) => row.status },
              { key: "torque", label: "Actual Torque", render: (row) => String(row.actual_torque ?? "-") },
              { key: "angle", label: "Actual Angle", render: (row) => String(row.actual_angle ?? "-") },
              { key: "file", label: "Source", render: (row) => row.source_file },
            ]}
            rows={executions.slice(0, 500)}
            rowKey={(row) => row.id}
          />

          <DataTable
            columns={[
              { key: "joint", label: "Joint", render: (row) => row.joint_id },
              { key: "bolt", label: "Bolt", render: (row) => row.bolt_no.toString() },
              { key: "status", label: "Failure", render: (row) => row.status },
              { key: "source", label: "Source", render: (row) => row.source_file },
            ]}
            rows={failedRows}
            rowKey={(row) => row.id}
            emptyLabel="No failed bolt rows found."
          />
        </>
      ) : null}

      {activeTab === "reports" ? (
        <DataTable
          columns={[
            { key: "type", label: "Type", render: (row) => row.report_type },
            { key: "wo", label: "Work Order", render: (row) => row.work_order_id ?? "-" },
            { key: "joint", label: "Joint", render: (row) => row.joint_id ?? "-" },
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
