"""
Pydantic schemas for user-related operations.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: str
    user_type: str = Field(..., pattern="^(student|counselor|admin)$")
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserRegister(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (excludes password)."""
    user_id: str
    created_at: str
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None


class StudentProfile(BaseModel):
    """Extended profile for students."""
    academic_level: Optional[str] = None
    field_of_interest: Optional[List[str]] = None
    target_countries: Optional[List[str]] = None
    budget_range: Optional[str] = None
    test_scores: Optional[dict] = None


class CounselorProfile(BaseModel):
    """Extended profile for counselors."""
    expertise_areas: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    years_experience: Optional[int] = None
    education: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = None
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    total_reviews: Optional[int] = Field(default=0, ge=0)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    token: str
    user: UserResponse


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: str
    new_password: str = Field(..., min_length=6)
