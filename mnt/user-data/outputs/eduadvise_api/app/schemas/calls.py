"""
Pydantic schemas for calls and WebRTC signaling.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CallInitiate(BaseModel):
    """Schema for initiating a call."""
    receiver_id: str
    call_type: str = Field(..., pattern="^(audio|video)$")


class CallResponse(BaseModel):
    """Schema for call response."""
    call_id: str
    caller_id: str
    receiver_id: str
    call_type: str
    status: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    created_at: str


class CallUpdate(BaseModel):
    """Schema for updating call status."""
    status: str = Field(..., pattern="^(ringing|accepted|declined|ended|missed)$")


class WebRTCSignal(BaseModel):
    """Schema for WebRTC signaling data."""
    type: str = Field(..., pattern="^(offer|answer|ice-candidate)$")
    data: Dict[str, Any]


class WebRTCConfig(BaseModel):
    """Schema for WebRTC configuration."""
    iceServers: list = Field(default_factory=list)


class CallNotification(BaseModel):
    """Schema for call notification via WebSocket."""
    type: str = "incoming_call"
    call_id: str
    caller_id: str
    caller_name: str
    call_type: str
