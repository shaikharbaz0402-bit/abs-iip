from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class TenantWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, tenant_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[tenant_id].add(websocket)

    def disconnect(self, tenant_id: str, websocket: WebSocket) -> None:
        if tenant_id in self._connections:
            self._connections[tenant_id].discard(websocket)
            if not self._connections[tenant_id]:
                del self._connections[tenant_id]

    async def broadcast(self, tenant_id: str, payload: dict) -> None:
        for ws in list(self._connections.get(tenant_id, set())):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(tenant_id, ws)


ws_manager = TenantWebSocketManager()
