"""
Pydantic schemas for bookings and services.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ServiceCreate(BaseModel):
    """Schema for creating a service."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str
    price: float = Field(..., ge=0)
    duration_minutes: int = Field(..., ge=15)
    service_type: str = Field(..., pattern="^(one-time|package)$")
    is_active: bool = True


class ServiceResponse(BaseModel):
    """Schema for service response."""
    service_id: str
    counselor_id: str
    name: str
    description: str
    price: float
    duration_minutes: int
    service_type: str
    is_active: bool
    created_at: str


class BookingCreate(BaseModel):
    """Schema for creating a booking."""
    service_id: str
    counselor_id: str
    session_date: str  # ISO format datetime
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    """Schema for booking response."""
    booking_id: str
    student_id: str
    counselor_id: str
    service_id: str
    session_date: str
    duration_minutes: int
    status: str
    payment_status: str
    amount: float
    notes: Optional[str] = None
    google_event_id: Optional[str] = None
    created_at: str


class BookingUpdate(BaseModel):
    """Schema for updating a booking."""
    status: Optional[str] = Field(None, pattern="^(pending|confirmed|cancelled|completed)$")
    session_date: Optional[str] = None
    notes: Optional[str] = None


class AvailabilitySlot(BaseModel):
    """Schema for counselor availability slot."""
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format


class AvailabilityCreate(BaseModel):
    """Schema for creating availability."""
    slots: List[AvailabilitySlot]


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""
    availability_id: str
    counselor_id: str
    slots: List[AvailabilitySlot]
    created_at: str
    updated_at: str
