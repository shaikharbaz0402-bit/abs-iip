import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface DataPoint {
  status?: string;
  count?: number;
}

export const TorqueDistributionChart = ({ data }: { data: DataPoint[] }) => {
  const normalized = data.map((item, index) => ({
    label: item.status || `Band ${index + 1}`,
    value: Number(item.count || 0),
  }));

  return (
    <div className="panel h-80 p-4">
      <h3 className="panel-title mb-3">Torque Distribution</h3>
      <ResponsiveContainer>
        <BarChart data={normalized}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="label" stroke="var(--color-text-muted)" />
          <YAxis stroke="var(--color-text-muted)" />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-panel)",
              border: "1px solid var(--color-border)",
            }}
          />
          <Legend />
          <Bar dataKey="value" fill="var(--color-accent)" name="Bolts" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
