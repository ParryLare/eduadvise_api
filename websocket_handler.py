"""
WebSocket endpoint for real-time communication.
"""
from fastapi import WebSocket, WebSocketDisconnect
from app.services.websocket import manager
import logging

logger = logging.getLogger(__name__)


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket connection handler for real-time chat and call signaling.
    
    Args:
        websocket: WebSocket connection
        user_id: User identifier
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif msg_type == "join_conversation":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    manager.join_room(conversation_id, user_id)
            
            elif msg_type == "leave_conversation":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    manager.leave_room(conversation_id, user_id)
            
            elif msg_type == "typing":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    await manager.broadcast_to_room(conversation_id, {
                        "type": "user_typing",
                        "user_id": user_id
                    }, exclude_user=user_id)
            
            elif msg_type == "stop_typing":
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    await manager.broadcast_to_room(conversation_id, {
                        "type": "user_stop_typing",
                        "user_id": user_id
                    }, exclude_user=user_id)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(user_id)
