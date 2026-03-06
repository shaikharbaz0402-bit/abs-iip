import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { ApiError, apiClient } from "@/api/apiClient";
import { authApi } from "@/services/absApi";
import { tenantStore } from "@/services/tenantStore";
import { tokenStore } from "@/services/tokenStore";
import type { PortalKind, UserProfile } from "@/types/domain";
import { isTokenExpired } from "@/utils/jwt";
import { getPortalFromRole } from "@/utils/roles";

interface AuthContextValue {
  token: string | null;
  user: UserProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  activePortal: PortalKind | null;
  activeTenantId: string;
  setActiveTenantId: (tenantId: string) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(() => tokenStore.get());
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTenantId, setActiveTenantIdState] = useState<string>(() => tenantStore.get() || "");

  const logout = useCallback(() => {
    tokenStore.clear();
    tenantStore.clear();
    setToken(null);
    setUser(null);
    setActiveTenantIdState("");
  }, []);

  const setActiveTenantId = useCallback((tenantId: string) => {
    setActiveTenantIdState(tenantId);
    if (tenantId) {
      tenantStore.set(tenantId);
    } else {
      tenantStore.clear();
    }
  }, []);

  useEffect(() => {
    apiClient.configureAuth(
      () => tokenStore.get(),
      async () => {
        const current = tokenStore.get();
        if (!current || isTokenExpired(current)) {
          tokenStore.clear();
          return null;
        }
        return current;
      },
      () => {
        logout();
      },
    );
  }, [logout]);

  useEffect(() => {
    apiClient.configureTenant(() => activeTenantId || null);
  }, [activeTenantId]);

  const bootstrap = useCallback(async () => {
    const storedToken = tokenStore.get();
    if (!storedToken || isTokenExpired(storedToken)) {
      logout();
      setLoading(false);
      return;
    }

    setToken(storedToken);

    try {
      const profile = await authApi.me();
      setUser(profile);

      const storedTenant = tenantStore.get();
      setActiveTenantId(storedTenant || profile.tenant_id);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  }, [logout, setActiveTenantId]);

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  const login = useCallback(
    async (email: string, password: string) => {
      const data = await authApi.login(email, password);
      tokenStore.set(data.access_token);
      setToken(data.access_token);

      const profile = await authApi.me();
      setUser(profile);
      setActiveTenantId(profile.tenant_id);
    },
    [setActiveTenantId],
  );

  const value = useMemo<AuthContextValue>(() => {
    return {
      token,
      user,
      loading,
      login,
      logout,
      activePortal: user ? getPortalFromRole(user.role) : null,
      activeTenantId,
      setActiveTenantId,
    };
  }, [token, user, loading, login, logout, activeTenantId, setActiveTenantId]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
