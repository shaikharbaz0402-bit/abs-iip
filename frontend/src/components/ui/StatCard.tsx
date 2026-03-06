import type { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: string;
  subtext?: string;
  tone?: "normal" | "danger";
  icon?: ReactNode;
}

export const StatCard = ({ label, value, subtext, tone = "normal", icon }: StatCardProps) => {
  return (
    <div className="panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="metric-label">{label}</p>
        {icon ? <span className="text-textMuted">{icon}</span> : null}
      </div>
      <p className={`metric-value ${tone === "danger" ? "text-accentAlt" : "text-text"}`}>{value}</p>
      {subtext ? <p className="mt-2 text-xs text-textMuted">{subtext}</p> : null}
    </div>
  );
};
