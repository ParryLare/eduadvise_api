"""
Pydantic schemas for messaging and chat operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    receiver_id: str
    content: str = Field(..., min_length=1)
    file_url: Optional[str] = None
    file_name: Optional[str] = None


class MessageResponse(BaseModel):
    """Schema for message response."""
    message_id: str
    conversation_id: str
    sender_id: str
    receiver_id: str
    content: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    is_read: bool
    created_at: str


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    conversation_id: str
    participants: List[str]
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0
    created_at: str
    updated_at: str


class ConversationWithDetails(ConversationResponse):
    """Conversation with participant details."""
    participant_details: Optional[List[dict]] = None


class TypingIndicator(BaseModel):
    """Schema for typing indicator websocket message."""
    type: str = Field(default="typing")
    conversation_id: str
    user_id: str
