import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/auth/AuthContext";
import type { DashboardRealtimeEvent } from "@/types/domain";

const resolveWsBase = () => {
  const raw = import.meta.env.VITE_API_BASE_URL || "https://abs-iip-production.up.railway.app";
  return raw.startsWith("https://") ? raw.replace("https://", "wss://") : raw.replace("http://", "ws://");
};

export const useDashboardRealtime = () => {
  const { token } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<DashboardRealtimeEvent | null>(null);

  const wsUrl = useMemo(() => {
    if (!token) return "";
    return `${resolveWsBase().replace(/\/$/, "")}/api/v1/dashboard/ws?token=${encodeURIComponent(token)}`;
  }, [token]);

  useEffect(() => {
    if (!wsUrl) {
      setIsConnected(false);
      return;
    }

    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setIsConnected(true);
      socket.send("ping");
    };

    socket.onclose = () => {
      setIsConnected(false);
    };

    socket.onerror = () => {
      setIsConnected(false);
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as DashboardRealtimeEvent;
        setLastEvent(payload);
      } catch {
        // Ignore malformed payloads from any non-standard upstream event.
      }
    };

    const heartbeat = window.setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send("ping");
      }
    }, 15000);

    return () => {
      window.clearInterval(heartbeat);
      socket.close();
    };
  }, [wsUrl]);

  return { isConnected, lastEvent };
};
