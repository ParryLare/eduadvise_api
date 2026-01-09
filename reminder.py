"""
In-app reminder service for booking notifications.
"""
from datetime import datetime, timezone
from typing import List
from app.core.database import get_database
from app.services.websocket import manager
import uuid
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    """Service to manage in-app reminders and notifications."""
    
    @staticmethod
    async def create_reminder(
        user_id: str, 
        booking_id: str, 
        reminder_time: datetime,
        reminder_type: str, 
        message: str
    ) -> dict:
        """
        Create a new reminder.
        
        Args:
            user_id: User to remind
            booking_id: Associated booking
            reminder_time: When to send reminder
            reminder_type: Type of reminder (24h, 1h, now)
            message: Reminder message
            
        Returns:
            Created reminder document
        """
        db = get_database()
        reminder = {
            "reminder_id": f"reminder_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "booking_id": booking_id,
            "reminder_time": reminder_time.isoformat(),
            "reminder_type": reminder_type,
            "message": message,
            "is_sent": False,
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.reminders.insert_one(reminder)
        logger.info(f"Created reminder {reminder['reminder_id']} for user {user_id}")
        return reminder
    
    @staticmethod
    async def get_pending_reminders(user_id: str) -> List[dict]:
        """
        Get all pending (unread) reminders for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of reminder documents
        """
        db = get_database()
        reminders = await db.reminders.find(
            {"user_id": user_id, "is_read": False},
            {"_id": 0}
        ).sort("reminder_time", 1).to_list(100)
        return reminders
    
    @staticmethod
    async def mark_reminder_read(reminder_id: str):
        """
        Mark a reminder as read.
        
        Args:
            reminder_id: Reminder identifier
        """
        db = get_database()
        await db.reminders.update_one(
            {"reminder_id": reminder_id},
            {"$set": {"is_read": True}}
        )
        logger.info(f"Marked reminder {reminder_id} as read")
    
    @staticmethod
    async def send_reminder_to_user(reminder: dict):
        """
        Send a reminder to user via WebSocket if online.
        
        Args:
            reminder: Reminder document
        """
        user_id = reminder["user_id"]
        
        # Send via WebSocket if user is online
        if manager.is_user_online(user_id):
            await manager.send_personal_message({
                "type": "reminder",
                "reminder": reminder
            }, user_id)
        
        # Mark as sent
        db = get_database()
        await db.reminders.update_one(
            {"reminder_id": reminder["reminder_id"]},
            {"$set": {"is_sent": True}}
        )
        logger.info(f"Sent reminder {reminder['reminder_id']} to user {user_id}")
    
    @staticmethod
    async def process_due_reminders():
        """
        Process and send all due reminders.
        
        This should be called by a background task/scheduler.
        """
        db = get_database()
        now = datetime.now(timezone.utc).isoformat()
        
        # Find reminders that are due and not sent
        due_reminders = await db.reminders.find(
            {
                "reminder_time": {"$lte": now},
                "is_sent": False
            },
            {"_id": 0}
        ).to_list(100)
        
        for reminder in due_reminders:
            try:
                await ReminderService.send_reminder_to_user(reminder)
            except Exception as e:
                logger.error(f"Error sending reminder {reminder['reminder_id']}: {e}")


# Global reminder service instance
reminder_service = ReminderService()
