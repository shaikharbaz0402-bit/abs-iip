import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
}

const variantClass: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary: "bg-accent text-white hover:opacity-90",
  secondary: "bg-panelSoft text-text border border-border hover:bg-panel",
  danger: "bg-accentAlt text-white hover:opacity-90",
  ghost: "bg-transparent text-text hover:bg-panelSoft",
};

export const Button = ({ variant = "primary", className = "", ...props }: ButtonProps) => {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-lg px-3 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${variantClass[variant]} ${className}`}
      {...props}
    />
  );
};
