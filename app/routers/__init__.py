"""
API route handlers.
"""
from app.routers.auth import router as auth_router
from app.routers.messages import router as messages_router
from app.routers.calls import router as calls_router
from app.routers.files import router as files_router

__all__ = [
    "auth_router",
    "messages_router",
    "calls_router",
    "files_router",
]
