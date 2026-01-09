"""
Authentication and user management routes.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from app.core.database import get_database
from app.core.security import Security, get_current_user
from app.schemas.users import (
    UserRegister, UserLogin, UserResponse, 
    TokenResponse, UserUpdate, PasswordChange
)
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
        
    Returns:
        Authentication token and user details
    """
    db = get_database()
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = Security.hash_password(user_data.password)
    
    # Create user document
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "user_type": user_data.user_type,
        "phone": user_data.phone,
        "country": user_data.country,
        "timezone": user_data.timezone,
        "avatar_url": user_data.avatar_url,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    logger.info(f"New user registered: {user_id} ({user_data.email})")
    
    # Create JWT token
    token = Security.create_jwt_token(user_id, user_data.email, user_data.user_type)
    
    # Remove password from response
    user_doc.pop("password")
    user_doc.pop("_id")
    
    return TokenResponse(
        token=token,
        user=UserResponse(**user_doc)
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """
    Authenticate a user and return access token.
    
    Args:
        credentials: User login credentials
        
    Returns:
        Authentication token and user details
    """
    db = get_database()
    
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not Security.verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if account is active
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Create JWT token
    token = Security.create_jwt_token(
        user["user_id"], 
        user["email"], 
        user["user_type"]
    )
    
    logger.info(f"User logged in: {user['user_id']} ({user['email']})")
    
    # Remove password and _id from response
    user.pop("password")
    user.pop("_id")
    
    return TokenResponse(
        token=token,
        user=UserResponse(**user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(request: Request):
    """
    Get current authenticated user profile.
    
    Returns:
        User profile data
    """
    user = await get_current_user(request)
    return UserResponse(**user)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(request: Request, update_data: UserUpdate):
    """
    Update current user profile.
    
    Args:
        update_data: Fields to update
        
    Returns:
        Updated user profile
    """
    user = await get_current_user(request)
    db = get_database()
    
    # Prepare update data (exclude None values)
    update_fields = update_data.model_dump(exclude_none=True)
    
    if not update_fields:
        return UserResponse(**user)
    
    # Update user in database
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": update_fields}
    )
    
    # Fetch updated user
    updated_user = await db.users.find_one(
        {"user_id": user["user_id"]}, 
        {"_id": 0, "password": 0}
    )
    
    logger.info(f"User profile updated: {user['user_id']}")
    
    return UserResponse(**updated_user)


@router.post("/change-password")
async def change_password(request: Request, password_data: PasswordChange):
    """
    Change user password.
    
    Args:
        password_data: Old and new password
        
    Returns:
        Success message
    """
    user = await get_current_user(request)
    db = get_database()
    
    # Get user with password
    user_with_password = await db.users.find_one({"user_id": user["user_id"]})
    
    # Verify old password
    if not Security.verify_password(password_data.old_password, user_with_password["password"]):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    # Hash new password
    new_hashed_password = Security.hash_password(password_data.new_password)
    
    # Update password
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"password": new_hashed_password}}
    )
    
    logger.info(f"Password changed for user: {user['user_id']}")
    
    return {"message": "Password changed successfully"}
