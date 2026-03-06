const TENANT_KEY = "abs_iip_active_tenant";

export const tenantStore = {
  get(): string | null {
    return localStorage.getItem(TENANT_KEY);
  },
  set(tenantId: string): void {
    localStorage.setItem(TENANT_KEY, tenantId);
  },
  clear(): void {
    localStorage.removeItem(TENANT_KEY);
  },
};
