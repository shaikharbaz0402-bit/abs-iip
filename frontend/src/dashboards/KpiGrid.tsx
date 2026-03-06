import { StatCard } from "@/components/ui/StatCard";
import type { KPIResponse } from "@/types/domain";
import { formatNumber, formatPercent } from "@/utils/format";

export const KpiGrid = ({ kpis }: { kpis: KPIResponse }) => {
  const failed = Math.max(kpis.total_joints - kpis.certified_joints - kpis.pending_joints, 0);

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-5">
      <StatCard label="Total Joints" value={formatNumber(kpis.total_joints)} />
      <StatCard label="Certified" value={formatNumber(kpis.certified_joints)} />
      <StatCard label="Pending" value={formatNumber(kpis.pending_joints)} />
      <StatCard label="Completion" value={formatPercent(kpis.completion_percentage, 2)} />
      <StatCard label="Failed Joints" value={formatNumber(failed)} tone={failed > 0 ? "danger" : "normal"} />
    </div>
  );
};
