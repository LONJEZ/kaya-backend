"""WebSocket support for real-time updates"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "subscribe":
                # Subscribe to updates
                await websocket.send_json({
                    "type": "subscribed",
                    "channels": message.get("channels", [])
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def notify_data_update(user_id: str, update_type: str):
    """Notify clients of data updates"""
    await manager.broadcast({
        "type": "data_update",
        "user_id": user_id,
        "update_type": update_type,
        "timestamp": "2025-10-20T00:00:00Z"
    })
