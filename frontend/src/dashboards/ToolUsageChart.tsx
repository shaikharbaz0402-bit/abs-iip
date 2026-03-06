import { Pie, PieChart, ResponsiveContainer, Tooltip, Cell } from "recharts";

import type { ToolHealthPoint } from "@/types/domain";

const COLORS = ["#0ea5e9", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#14b8a6"];

export const ToolUsageChart = ({ data }: { data: ToolHealthPoint[] }) => {
  const chartData = data.map((item) => ({
    name: item.tool_code,
    value: item.total_cycles,
  }));

  return (
    <div className="panel h-80 p-4">
      <h3 className="panel-title mb-3">Tool Usage</h3>
      <ResponsiveContainer>
        <PieChart>
          <Pie dataKey="value" data={chartData} innerRadius={55} outerRadius={100} label>
            {chartData.map((entry, index) => (
              <Cell key={`${entry.name}-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-panel)",
              border: "1px solid var(--color-border)",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
