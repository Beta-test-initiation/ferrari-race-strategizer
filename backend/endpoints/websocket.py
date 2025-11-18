"""WebSocket endpoints for real-time updates."""

import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

# Keep track of connected clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")


manager = ConnectionManager()


@router.websocket("/ws/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time race updates.

    Sends:
    - Race state updates (every 5-10 seconds)
    - Live alerts
    - Strategy recommendation updates
    - Weather changes

    Client can send:
    - {"type": "ping"} to check connection
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await manager.send_personal(
            websocket,
            {
                "type": "CONNECTED",
                "message": "Connected to live updates",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

        # Send initial race state
        await manager.send_personal(
            websocket,
            {
                "type": "RACE_STATE_UPDATE",
                "data": {
                    "current_lap": 25,
                    "position": 3,
                    "tire_age": 20,
                    "compound": "MEDIUM",
                    "track_temp": 35.0,
                    "gap_to_leader": 2.1,
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

        # Listen for client messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_personal(
                        websocket,
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat() + "Z"},
                    )
                    logger.debug("Ping received and pong sent")
                else:
                    logger.info(f"Received message: {message}")

            except asyncio.TimeoutError:
                # Send heartbeat every 30 seconds if no message
                await manager.send_personal(
                    websocket,
                    {
                        "type": "HEARTBEAT",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alerts.

    Sends:
    - Pit window alerts
    - Tire degradation alerts
    - DRS availability alerts
    - Strategy update alerts
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await manager.send_personal(
            websocket,
            {
                "type": "ALERTS_CONNECTED",
                "message": "Connected to alerts",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_personal(
                        websocket,
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat() + "Z"},
                    )

            except asyncio.TimeoutError:
                # Send heartbeat
                await manager.send_personal(
                    websocket,
                    {
                        "type": "HEARTBEAT",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from alerts")
    except Exception as e:
        logger.error(f"Alerts WebSocket error: {e}")
        manager.disconnect(websocket)


def get_manager():
    """Get the connection manager instance."""
    return manager
