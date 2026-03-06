import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import type { PortalKind } from "@/types/domain";
import { getPortalPath } from "@/utils/roles";

interface ProtectedRouteProps {
  allowedPortal: PortalKind;
  children: JSX.Element;
}

export const ProtectedRoute = ({ allowedPortal, children }: ProtectedRouteProps) => {
  const { loading, token, user, activePortal } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-textMuted">
        Loading session...
      </div>
    );
  }

  if (!token || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (activePortal !== allowedPortal) {
    return <Navigate to={activePortal ? getPortalPath(activePortal) : "/login"} replace />;
  }

  return children;
};
