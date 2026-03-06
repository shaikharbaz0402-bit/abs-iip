import type { PortalKind, UserRole } from "@/types/domain";

export const rolePortalMap: Record<UserRole, PortalKind> = {
  SUPER_ADMIN: "admin",
  ABS_ENGINEER: "admin",
  CLIENT_ADMIN: "manager",
  CLIENT_ENGINEER: "operator",
  CLIENT_VIEWER: "client",
};

export const getPortalPath = (portal: PortalKind): string => {
  switch (portal) {
    case "admin":
      return "/admin";
    case "manager":
      return "/manager";
    case "operator":
      return "/operator";
    case "client":
      return "/client";
    default:
      return "/login";
  }
};

export const getPortalFromRole = (role: UserRole): PortalKind => rolePortalMap[role];
