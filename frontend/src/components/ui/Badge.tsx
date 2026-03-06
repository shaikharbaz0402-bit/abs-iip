import type { PropsWithChildren } from "react";

interface BadgeProps extends PropsWithChildren {
  tone?: "neutral" | "success" | "warning" | "danger" | "info";
}

const tones: Record<NonNullable<BadgeProps["tone"]>, string> = {
  neutral: "bg-panelSoft text-textMuted",
  success: "bg-emerald-500/15 text-emerald-300",
  warning: "bg-amber-500/20 text-amber-200",
  danger: "bg-rose-500/20 text-rose-200",
  info: "bg-cyan-500/20 text-cyan-200",
};

export const Badge = ({ tone = "neutral", children }: BadgeProps) => {
  return <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${tones[tone]}`}>{children}</span>;
};
