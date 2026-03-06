import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { Execution } from "@/types/domain";

const bucketBySource = (executions: Execution[]) => {
  const grouped = new Map<string, { source: string; failed: number; total: number }>();

  executions.forEach((execution) => {
    const key = execution.source_file || "Unknown";
    const current = grouped.get(key) || { source: key, failed: 0, total: 0 };
    current.total += 1;
    if (execution.status === "NOK" || execution.status === "OutOfTolerance") {
      current.failed += 1;
    }
    grouped.set(key, current);
  });

  return Array.from(grouped.values())
    .slice(0, 10)
    .map((item) => ({
      source: item.source,
      failureRate: item.total ? Number(((item.failed / item.total) * 100).toFixed(2)) : 0,
    }));
};

export const FailureTrendChart = ({ executions }: { executions: Execution[] }) => {
  const series = bucketBySource(executions);

  return (
    <div className="panel h-80 p-4">
      <h3 className="panel-title mb-3">Failure Rate Trend</h3>
      <ResponsiveContainer>
        <LineChart data={series}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="source" stroke="var(--color-text-muted)" tick={false} />
          <YAxis stroke="var(--color-text-muted)" unit="%" />
          <Tooltip
            formatter={(value: number) => `${value}%`}
            contentStyle={{
              backgroundColor: "var(--color-panel)",
              border: "1px solid var(--color-border)",
            }}
          />
          <Line type="monotone" dataKey="failureRate" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
