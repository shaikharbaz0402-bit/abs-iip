interface HeatCell {
  joint_id?: string;
  bolt_no?: number;
  status?: string;
}

const valueByStatus = (status: string): string => {
  if (status === "OK") return "bg-emerald-500/80";
  if (status === "NOK") return "bg-rose-500/80";
  if (status === "OutOfTolerance") return "bg-amber-400/80";
  return "bg-slate-500/60";
};

export const JointHeatmap = ({ rows }: { rows: HeatCell[] }) => {
  if (!rows.length) {
    return (
      <div className="panel p-4">
        <h3 className="panel-title">Joint Completion Heatmap</h3>
        <p className="mt-2 text-sm text-textMuted">No heatmap data available.</p>
      </div>
    );
  }

  const limited = rows.slice(0, 180);

  return (
    <div className="panel p-4">
      <h3 className="panel-title mb-3">Joint Completion Heatmap</h3>
      <div className="grid grid-cols-12 gap-1">
        {limited.map((row, index) => (
          <div
            key={`${row.joint_id}-${row.bolt_no}-${index}`}
            className={`h-4 w-4 rounded-sm ${valueByStatus(row.status || "Missing")}`}
            title={`${row.joint_id || "Joint"} - B${row.bolt_no || 0}: ${row.status || "Missing"}`}
          />
        ))}
      </div>
    </div>
  );
};
