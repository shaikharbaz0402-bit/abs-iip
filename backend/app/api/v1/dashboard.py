from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import tenant_context_read
from app.core.deps import TenantContext
from app.core.security import decode_token
from app.db.session import get_db
from app.models.joint import Joint
from app.services.websocket_manager import ws_manager

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/client-progress")
def client_progress(
    project_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(tenant_context_read),
) -> dict:
    stmt = select(Joint).where(Joint.tenant_id == ctx.tenant_id)
    if project_id:
        stmt = stmt.where(Joint.project_id == project_id)

    joints = db.scalars(stmt).all()
    total = len(joints)
    certified = sum(1 for joint in joints if joint.status.value == "Certified")

    return {
        "total_joints": total,
        "certified_joints": certified,
        "completion_percentage": round((certified / total) * 100, 2) if total else 0.0,
        "items": [
            {"joint_id": joint.joint_id, "status": joint.status.value, "project_id": joint.project_id}
            for joint in joints
        ],
    }


@router.websocket("/ws")
async def websocket_dashboard(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token", "")
    if not token:
        await websocket.close(code=4401)
        return

    try:
        payload = decode_token(token)
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise ValueError("Missing tenant")
    except Exception:
        await websocket.close(code=4401)
        return

    await ws_manager.connect(tenant_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(tenant_id, websocket)
