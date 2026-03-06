import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { AuthProvider, useAuth } from "@/auth/AuthContext";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { ThemeProvider } from "@/hooks/useTheme";
import { AdminPortalPage } from "@/pages/AdminPortalPage";
import { ClientPortalPage } from "@/pages/ClientPortalPage";
import { LoginPage } from "@/pages/LoginPage";
import { ManagerPortalPage } from "@/pages/ManagerPortalPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { OperatorPortalPage } from "@/pages/OperatorPortalPage";
import { getPortalPath } from "@/utils/roles";

const HomeRedirect = () => {
  const { activePortal, loading } = useAuth();

  if (loading) {
    return <div className="p-6 text-textMuted">Loading...</div>;
  }

  if (!activePortal) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={getPortalPath(activePortal)} replace />;
};

export const App = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/" element={<HomeRedirect />} />
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedPortal="admin">
                  <AdminPortalPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/manager"
              element={
                <ProtectedRoute allowedPortal="manager">
                  <ManagerPortalPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/operator"
              element={
                <ProtectedRoute allowedPortal="operator">
                  <OperatorPortalPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/client"
              element={
                <ProtectedRoute allowedPortal="client">
                  <ClientPortalPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};
