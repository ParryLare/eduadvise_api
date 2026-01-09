"""
Email notification service for user communications.
"""
from datetime import datetime, timezone
from app.core.database import get_database
import uuid
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """
    Email notification service.
    
    This is a mock implementation that logs emails to the database
    instead of actually sending them. In production, integrate with
    an email service provider like SendGrid, AWS SES, or Mailgun.
    """
    
    @staticmethod
    async def log_email(to_email: str, subject: str, body: str, email_type: str) -> dict:
        """
        Store email in database for tracking.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            email_type: Type/category of email
            
        Returns:
            Email log document
        """
        db = get_database()
        email_log = {
            "email_id": f"email_{uuid.uuid4().hex[:12]}",
            "to_email": to_email,
            "subject": subject,
            "body": body,
            "email_type": email_type,
            "status": "logged",  # In production: pending, sent, failed
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.email_logs.insert_one(email_log)
        logger.info(f"[EMAIL] To: {to_email} | Subject: {subject} | Type: {email_type}")
        return email_log
    
    @staticmethod
    async def send_new_message_notification(
        to_email: str, 
        sender_name: str, 
        message_preview: str
    ) -> dict:
        """Send notification for new message."""
        subject = f"New message from {sender_name} - EduAdvise"
        body = f"""
Hello,

You have a new message from {sender_name}:

"{message_preview[:100]}{'...' if len(message_preview) > 100 else ''}"

Log in to EduAdvise to read and reply.

Best regards,
EduAdvise Team
        """
        return await EmailNotificationService.log_email(
            to_email, subject, body, "new_message"
        )
    
    @staticmethod
    async def send_incoming_call_notification(
        to_email: str, 
        caller_name: str, 
        call_type: str
    ) -> dict:
        """Send notification for missed call."""
        subject = f"Missed {call_type} call from {caller_name} - EduAdvise"
        body = f"""
Hello,

You missed a {call_type} call from {caller_name} on EduAdvise.

Log in to EduAdvise to connect with them.

Best regards,
EduAdvise Team
        """
        return await EmailNotificationService.log_email(
            to_email, subject, body, "missed_call"
        )
    
    @staticmethod
    async def send_booking_reminder(
        to_email: str, 
        user_name: str, 
        other_party_name: str,
        service_name: str, 
        session_time: str, 
        hours_before: int
    ) -> dict:
        """Send booking reminder notification."""
        subject = f"Reminder: Session in {hours_before} hour{'s' if hours_before > 1 else ''} - EduAdvise"
        reminder_text = (
            'Please be ready to join the video call on time.' 
            if hours_before == 1 
            else 'Make sure you have prepared any questions or documents you want to discuss.'
        )
        body = f"""
Hello {user_name},

This is a reminder that your session is coming up:

Service: {service_name}
With: {other_party_name}
Time: {session_time}

{reminder_text}

Best regards,
EduAdvise Team
        """
        return await EmailNotificationService.log_email(
            to_email, subject, body, f"reminder_{hours_before}h"
        )
    
    @staticmethod
    async def send_booking_confirmation(
        to_email: str, 
        user_name: str, 
        service_name: str,
        counselor_name: str, 
        session_time: str
    ) -> dict:
        """Send booking confirmation notification."""
        subject = f"Booking Confirmed - {service_name} - EduAdvise"
        body = f"""
Hello {user_name},

Your booking has been confirmed!

Service: {service_name}
Counselor: {counselor_name}
Time: {session_time}

You will receive reminders 24 hours and 1 hour before your session.

Best regards,
EduAdvise Team
        """
        return await EmailNotificationService.log_email(
            to_email, subject, body, "booking_confirmed"
        )


# Global email service instance
email_service = EmailNotificationService()
