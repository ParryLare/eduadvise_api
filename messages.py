"""
Messaging and chat routes.
"""
from fastapi import APIRouter, HTTPException, Request
from app.core.database import get_database
from app.core.security import get_current_user
from app.schemas.messages import MessageCreate, MessageResponse, ConversationResponse
from app.services.websocket import manager
from app.services.email import email_service
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/send", response_model=MessageResponse)
async def send_message(request: Request, message_data: MessageCreate):
    """Send a message to another user."""
    user = await get_current_user(request)
    db = get_database()
    
    # Verify receiver exists
    receiver = await db.users.find_one({"user_id": message_data.receiver_id}, {"_id": 0})
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Create or get conversation
    conv_query = {
        "participants": {
            "$all": [user["user_id"], message_data.receiver_id]
        }
    }
    conversation = await db.conversations.find_one(conv_query, {"_id": 0})
    
    if not conversation:
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        conversation = {
            "conversation_id": conversation_id,
            "participants": [user["user_id"], message_data.receiver_id],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.conversations.insert_one(conversation)
    else:
        conversation_id = conversation["conversation_id"]
    
    # Create message
    message = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "conversation_id": conversation_id,
        "sender_id": user["user_id"],
        "receiver_id": message_data.receiver_id,
        "content": message_data.content,
        "file_url": message_data.file_url,
        "file_name": message_data.file_name,
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.messages.insert_one(message)
    await db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"updated_at": message["created_at"]}}
    )
    
    # Send via WebSocket if receiver is online
    if manager.is_user_online(message_data.receiver_id):
        await manager.send_personal_message({
            "type": "new_message",
            "message": message
        }, message_data.receiver_id)
    else:
        # Send email notification
        await email_service.send_new_message_notification(
            receiver["email"],
            user["full_name"],
            message_data.content
        )
    
    message.pop("_id", None)
    return MessageResponse(**message)


@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(request: Request):
    """Get all conversations for current user."""
    user = await get_current_user(request)
    db = get_database()
    
    conversations = await db.conversations.find(
        {"participants": user["user_id"]},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    
    result = []
    for conv in conversations:
        # Get last message
        last_msg = await db.messages.find_one(
            {"conversation_id": conv["conversation_id"]},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        
        # Count unread messages
        unread_count = await db.messages.count_documents({
            "conversation_id": conv["conversation_id"],
            "receiver_id": user["user_id"],
            "is_read": False
        })
        
        conv["last_message"] = last_msg
        conv["unread_count"] = unread_count
        result.append(ConversationResponse(**conv))
    
    return result


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(request: Request, conversation_id: str, limit: int = 50):
    """Get messages from a conversation."""
    user = await get_current_user(request)
    db = get_database()
    
    # Verify user is part of conversation
    conversation = await db.conversations.find_one({
        "conversation_id": conversation_id,
        "participants": user["user_id"]
    })
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Mark messages as read
    await db.messages.update_many(
        {
            "conversation_id": conversation_id,
            "receiver_id": user["user_id"],
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )
    
    return messages[::-1]  # Reverse to chronological order
