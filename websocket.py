"""
WebSocket connection manager for real-time communication.
"""
from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time features."""
    
    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # room_id -> list of user_ids
        self.chat_rooms: Dict[str, List[str]] = {}
        # For WebRTC signaling: user_id -> pending signals
        self.pending_signals: Dict[str, List[dict]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, user_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            user_id: User identifier
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """
        Send a message to a specific user.
        
        Args:
            message: Message data to send
            user_id: Target user identifier
        """
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        """
        Broadcast a message to all users in a room.
        
        Args:
            room_id: Room identifier
            message: Message data to broadcast
            exclude_user: Optional user_id to exclude from broadcast
        """
        if room_id in self.chat_rooms:
            for user_id in self.chat_rooms[room_id]:
                if user_id != exclude_user and user_id in self.active_connections:
                    await self.send_personal_message(message, user_id)
    
    def join_room(self, room_id: str, user_id: str):
        """
        Add a user to a chat room.
        
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = []
        if user_id not in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].append(user_id)
            logger.info(f"User {user_id} joined room {room_id}")
    
    def leave_room(self, room_id: str, user_id: str):
        """
        Remove a user from a chat room.
        
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        if room_id in self.chat_rooms and user_id in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].remove(user_id)
            logger.info(f"User {user_id} left room {room_id}")
    
    def is_user_online(self, user_id: str) -> bool:
        """
        Check if a user is currently online.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user is connected, False otherwise
        """
        return user_id in self.active_connections


# Global connection manager instance
manager = ConnectionManager()
