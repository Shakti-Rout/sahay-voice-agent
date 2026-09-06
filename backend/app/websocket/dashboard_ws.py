"""
Live Operator Triage Dashboard WebSocket Hub.
Broadcasts real-time call telemetry, live transcripts, distress fluctuations,
and critical escalation alerts to all connected operator workstations.
"""

import json
import logging
from typing import Any, Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class DashboardBroadcaster:
    """Singleton connection pool and event broadcaster for operator dashboards."""

    _instance = None

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    @classmethod
    def get_instance(cls) -> "DashboardBroadcaster":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"[DashboardWS] Operator connected. Total active operators: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"[DashboardWS] Operator disconnected. Remaining operators: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        """Broadcasts an event message to all connected operator dashboards."""
        if not self.active_connections:
            return

        payload = {
            "event": event_type,
            "data": data
        }
        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception as e:
                logger.warning(f"[DashboardWS] Failed to send to operator client: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)


broadcaster = DashboardBroadcaster.get_instance()


async def handle_dashboard_websocket(websocket: WebSocket):
    """FastAPI endpoint handler for /ws/dashboard."""
    await broadcaster.connect(websocket)
    try:
        # Initial greeting and health packet
        await websocket.send_json({
            "event": "operator_authenticated",
            "data": {
                "status": "connected",
                "badge": "OP-14566-CORE",
                "message": "Connected to NHAA (14566) Real-Time Operator Triage Dispatch Stream"
            }
        })
        while True:
            # Keep connection alive, receive operator commands (e.g. acknowledge escalation)
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                cmd = msg.get("command")
                if cmd == "ping":
                    await websocket.send_json({"event": "pong"})
            except Exception:
                pass
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
    except Exception as e:
        logger.error(f"[DashboardWS] Connection exception: {e}")
        broadcaster.disconnect(websocket)
