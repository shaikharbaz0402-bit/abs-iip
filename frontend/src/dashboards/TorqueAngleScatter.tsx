import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Point {
  actual_torque?: number;
  actual_angle?: number;
  status?: string;
}

const COLORS: Record<string, string> = {
  OK: "#22c55e",
  NOK: "#ef4444",
  Missing: "#94a3b8",
  OutOfTolerance: "#f59e0b",
};

export const TorqueAngleScatter = ({ points }: { points: Point[] }) => {
  const grouped = points.reduce<Record<string, Point[]>>((acc, point) => {
    const status = point.status || "Missing";
    if (!acc[status]) acc[status] = [];
    acc[status].push(point);
    return acc;
  }, {});

  return (
    <div className="panel h-80 p-4">
      <h3 className="panel-title mb-3">Torque vs Angle</h3>
      <ResponsiveContainer>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis type="number" dataKey="actual_angle" name="Angle" stroke="var(--color-text-muted)" />
          <YAxis type="number" dataKey="actual_torque" name="Torque" stroke="var(--color-text-muted)" />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-panel)",
              border: "1px solid var(--color-border)",
            }}
          />
          {Object.entries(grouped).map(([status, data]) => (
            <Scatter key={status} name={status} data={data} fill={COLORS[status] || "#2dd4bf"} />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};
