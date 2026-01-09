"""
Pydantic schemas for request/response validation.
"""
from app.schemas.users import (
    UserBase,
    UserRegister,
    UserLogin,
    UserResponse,
    UserUpdate,
    StudentProfile,
    CounselorProfile,
    TokenResponse,
    PasswordChange,
)
from app.schemas.messages import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
    ConversationWithDetails,
    TypingIndicator,
)
from app.schemas.bookings import (
    ServiceCreate,
    ServiceResponse,
    BookingCreate,
    BookingResponse,
    BookingUpdate,
    AvailabilitySlot,
    AvailabilityCreate,
    AvailabilityResponse,
)
from app.schemas.calls import (
    CallInitiate,
    CallResponse,
    CallUpdate,
    WebRTCSignal,
    WebRTCConfig,
    CallNotification,
)

__all__ = [
    # Users
    "UserBase",
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "StudentProfile",
    "CounselorProfile",
    "TokenResponse",
    "PasswordChange",
    # Messages
    "MessageCreate",
    "MessageResponse",
    "ConversationResponse",
    "ConversationWithDetails",
    "TypingIndicator",
    # Bookings
    "ServiceCreate",
    "ServiceResponse",
    "BookingCreate",
    "BookingResponse",
    "BookingUpdate",
    "AvailabilitySlot",
    "AvailabilityCreate",
    "AvailabilityResponse",
    # Calls
    "CallInitiate",
    "CallResponse",
    "CallUpdate",
    "WebRTCSignal",
    "WebRTCConfig",
    "CallNotification",
]
