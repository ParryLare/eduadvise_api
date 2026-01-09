"""
Video/audio call routes and WebRTC signaling.
"""
from fastapi import APIRouter, HTTPException, Request
from app.core.database import get_database
from app.core.security import get_current_user
from app.schemas.calls import CallInitiate, CallResponse, CallUpdate, WebRTCSignal
from app.services.websocket import manager
from app.services.email import email_service
from app.core.config import settings
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["Calls"])


@router.post("/initiate", response_model=CallResponse)
async def initiate_call(request: Request, call_data: CallInitiate):
    """Initiate a call to another user."""
    user = await get_current_user(request)
    db = get_database()
    
    # Verify receiver exists
    receiver = await db.users.find_one({"user_id": call_data.receiver_id}, {"_id": 0})
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create call session
    call = {
        "call_id": f"call_{uuid.uuid4().hex[:12]}",
        "caller_id": user["user_id"],
        "receiver_id": call_data.receiver_id,
        "call_type": call_data.call_type,
        "status": "ringing",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.call_sessions.insert_one(call)
    
    # Notify receiver via WebSocket
    if manager.is_user_online(call_data.receiver_id):
        await manager.send_personal_message({
            "type": "incoming_call",
            "call_id": call["call_id"],
            "caller_id": user["user_id"],
            "caller_name": user["full_name"],
            "call_type": call_data.call_type
        }, call_data.receiver_id)
    else:
        # Send email notification
        await email_service.send_incoming_call_notification(
            receiver["email"],
            user["full_name"],
            call_data.call_type
        )
    
    call.pop("_id", None)
    return CallResponse(**call)


@router.put("/{call_id}/status", response_model=CallResponse)
async def update_call_status(request: Request, call_id: str, status_data: CallUpdate):
    """Update call status (accept, decline, end)."""
    user = await get_current_user(request)
    db = get_database()
    
    call = await db.call_sessions.find_one({"call_id": call_id}, {"_id": 0})
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if user["user_id"] not in [call["caller_id"], call["receiver_id"]]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = {"status": status_data.status}
    
    if status_data.status == "accepted":
        update_data["started_at"] = datetime.now(timezone.utc).isoformat()
    elif status_data.status in ["ended", "declined", "missed"]:
        update_data["ended_at"] = datetime.now(timezone.utc).isoformat()
        if call.get("started_at"):
            started = datetime.fromisoformat(call["started_at"])
            ended = datetime.now(timezone.utc)
            update_data["duration_seconds"] = int((ended - started).total_seconds())
    
    await db.call_sessions.update_one(
        {"call_id": call_id},
        {"$set": update_data}
    )
    
    # Notify other party
    other_user_id = call["receiver_id"] if user["user_id"] == call["caller_id"] else call["caller_id"]
    await manager.send_personal_message({
        "type": "call_status_update",
        "call_id": call_id,
        "status": status_data.status
    }, other_user_id)
    
    updated_call = await db.call_sessions.find_one({"call_id": call_id}, {"_id": 0})
    return CallResponse(**updated_call)


@router.post("/{call_id}/signal")
async def send_webrtc_signal(request: Request, call_id: str, signal_data: WebRTCSignal):
    """Send WebRTC signaling data (offer/answer/ICE candidate)."""
    user = await get_current_user(request)
    db = get_database()
    
    call = await db.call_sessions.find_one({"call_id": call_id}, {"_id": 0})
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if user["user_id"] not in [call["caller_id"], call["receiver_id"]]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Send to other party
    other_user_id = call["receiver_id"] if user["user_id"] == call["caller_id"] else call["caller_id"]
    
    await manager.send_personal_message({
        "type": "webrtc_signal",
        "call_id": call_id,
        "signal_type": signal_data.type,
        "data": signal_data.data
    }, other_user_id)
    
    return {"message": "Signal sent"}


@router.get("/webrtc-config")
async def get_webrtc_config(request: Request):
    """Get WebRTC configuration including TURN servers."""
    await get_current_user(request)
    return {"iceServers": settings.TURN_SERVERS}


@router.get("/history")
async def get_call_history(request: Request, limit: int = 20):
    """Get call history for current user."""
    user = await get_current_user(request)
    db = get_database()
    
    calls = await db.call_sessions.find(
        {"$or": [{"caller_id": user["user_id"]}, {"receiver_id": user["user_id"]}]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return calls
