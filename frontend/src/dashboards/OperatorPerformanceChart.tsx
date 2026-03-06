import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { OperatorAnalyticsPoint } from "@/types/domain";

export const OperatorPerformanceChart = ({ data }: { data: OperatorAnalyticsPoint[] }) => {
  const top = [...data]
    .sort((a, b) => b.jobs_completed - a.jobs_completed)
    .slice(0, 8)
    .map((item) => ({
      name: item.name,
      jobs: item.jobs_completed,
    }));

  return (
    <div className="panel h-80 p-4">
      <h3 className="panel-title mb-3">Operator Productivity</h3>
      <ResponsiveContainer>
        <BarChart data={top}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="name" stroke="var(--color-text-muted)" tick={false} />
          <YAxis stroke="var(--color-text-muted)" />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-panel)",
              border: "1px solid var(--color-border)",
            }}
          />
          <Bar dataKey="jobs" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
