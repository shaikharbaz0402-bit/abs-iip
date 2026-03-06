import { type ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Button } from "@/components/ui/Button";

export interface PortalNavItem {
  id: string;
  label: string;
}

interface PortalLayoutProps {
  title: string;
  subtitle: string;
  navItems: PortalNavItem[];
  activeNav: string;
  onSelectNav: (id: string) => void;
  children: ReactNode;
  headerActions?: ReactNode;
}

export const PortalLayout = ({
  title,
  subtitle,
  navItems,
  activeNav,
  onSelectNav,
  children,
  headerActions,
}: PortalLayoutProps) => {
  const { user, logout, activeTenantId } = useAuth();

  return (
    <div className="min-h-screen bg-grid p-4 md:p-6">
      <div className="mx-auto grid max-w-[1680px] grid-cols-1 gap-4 lg:grid-cols-[270px_1fr]">
        <aside className="panel p-4">
          <p className="text-xs uppercase tracking-wider text-textMuted">ABS Industrial Platform</p>
          <h1 className="mt-2 text-xl font-bold text-text">{title}</h1>
          <p className="mt-1 text-sm text-textMuted">{subtitle}</p>

          <div className="mt-6 max-h-[45vh] space-y-2 overflow-auto pr-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectNav(item.id)}
                className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                  activeNav === item.id ? "bg-accent text-white" : "bg-panelSoft text-text hover:bg-panel"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="mt-6 rounded-lg border border-border bg-panelSoft p-3 text-xs text-textMuted">
            <p>{user?.full_name}</p>
            <p className="truncate">{user?.email}</p>
            <p className="mt-1 font-semibold text-text">{user?.role}</p>
            <p className="mt-1">Tenant: {activeTenantId || user?.tenant_id || "-"}</p>
          </div>

          <div className="mt-4 space-y-2">
            <ThemeToggle />
            <Button variant="danger" className="w-full" onClick={logout}>
              Logout
            </Button>
          </div>

          <div className="mt-6 text-xs text-textMuted">
            <NavLink to="/login" className="underline">
              Switch account
            </NavLink>
          </div>
        </aside>

        <main className="space-y-4">
          <div className="panel flex flex-col gap-3 p-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-wider text-textMuted">Enterprise Control Plane</p>
              <h2 className="text-lg font-semibold text-text">{title}</h2>
            </div>
            {headerActions ? <div className="flex flex-wrap items-center gap-2">{headerActions}</div> : null}
          </div>

          {children}
        </main>
      </div>
    </div>
  );
};
