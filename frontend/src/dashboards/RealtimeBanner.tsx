import { Badge } from "@/components/ui/Badge";
import type { DashboardRealtimeEvent } from "@/types/domain";

export const RealtimeBanner = ({
  connected,
  event,
}: {
  connected: boolean;
  event: DashboardRealtimeEvent | null;
}) => {
  return (
    <div className="panel flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-semibold text-text">Realtime Sync</p>
        <p className="text-xs text-textMuted">
          {event
            ? `Last event: ${event.event} | Joint ${event.joint_id || "-"} | Status ${event.status || "-"}`
            : "No realtime event received yet"}
        </p>
      </div>
      <Badge tone={connected ? "success" : "warning"}>{connected ? "Connected" : "Disconnected"}</Badge>
    </div>
  );
};
