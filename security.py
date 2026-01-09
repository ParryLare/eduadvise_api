"""
Security utilities for authentication and authorization.
"""
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Request
from app.core.config import settings
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)


class Security:
    """Security utilities for password hashing and JWT tokens."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def create_jwt_token(user_id: str, email: str, user_type: str) -> str:
        """Create a JWT token for user authentication."""
        expiration = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        payload = {
            "user_id": user_id,
            "email": email,
            "user_type": user_type,
            "exp": expiration
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode_jwt_token(token: str) -> Optional[Dict]:
        """Decode and verify a JWT token."""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None


async def get_current_user(request: Request) -> Dict:
    """
    Dependency function to get current authenticated user from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User dictionary with user_id, email, and user_type
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.replace("Bearer ", "")
    payload = Security.decode_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Verify user still exists in database
    db = get_database()
    user = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0, "password": 0})
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


async def require_user_type(*allowed_types: str):
    """
    Dependency factory to require specific user types.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_user_type("admin"))])
    """
    async def _check_user_type(user: Dict = Depends(get_current_user)):
        if user.get("user_type") not in allowed_types:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required user type: {', '.join(allowed_types)}"
            )
        return user
    return _check_user_type
