"""
Application configuration management.
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "EduAdvise - International Student Counseling Platform"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    
    # MongoDB
    MONGO_URL: str = Field(..., description="MongoDB connection URL")
    DB_NAME: str = Field(..., description="MongoDB database name")
    
    # JWT
    JWT_SECRET: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        description="Secret key for JWT token generation"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 168  # 7 days
    
    # Google Calendar (Optional)
    GOOGLE_CALENDAR_CLIENT_ID: str = ""
    GOOGLE_CALENDAR_CLIENT_SECRET: str = ""
    GOOGLE_CALENDAR_REDIRECT_URI: str = ""
    
    # TURN Server Configuration
    TURN_SERVERS: List[dict] = Field(
        default=[
            {
                "urls": "stun:stun.l.google.com:19302"
            },
            {
                "urls": "turn:your-turn-server.com:3478",
                "username": "user",
                "credential": "pass"
            }
        ]
    )
    
    # File Upload
    UPLOAD_DIR: Path = Field(default=Path("uploads"))
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', 
                                '.png', '.gif', '.txt', '.xlsx', '.xls'}
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(exist_ok=True)
