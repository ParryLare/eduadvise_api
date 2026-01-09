"""
File upload and download routes.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File as FastAPIFile, Response
from app.core.database import get_database
from app.core.security import get_current_user
from app.core.config import settings
from pathlib import Path
from datetime import datetime, timezone
import uuid
import aiofiles
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = FastAPIFile(...)):
    """Upload a file for chat sharing."""
    user = await get_current_user(request)
    db = get_database()
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read and validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    file_id = f"file_{uuid.uuid4().hex[:12]}"
    safe_filename = f"{file_id}{file_ext}"
    file_path = settings.UPLOAD_DIR / safe_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)
    
    # Store file metadata in database
    file_doc = {
        "file_id": file_id,
        "original_name": file.filename,
        "stored_name": safe_filename,
        "size": len(contents),
        "content_type": file.content_type,
        "uploaded_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.uploaded_files.insert_one(file_doc)
    file_doc.pop("_id", None)
    
    # Return file URL
    file_doc["url"] = f"/api/files/{safe_filename}"
    
    logger.info(f"File uploaded: {safe_filename} by user {user['user_id']}")
    return file_doc


@router.get("/{filename}")
async def get_file(filename: str):
    """Serve uploaded files."""
    file_path = settings.UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get content type from database
    db = get_database()
    file_doc = await db.uploaded_files.find_one({"stored_name": filename}, {"_id": 0})
    content_type = file_doc["content_type"] if file_doc else "application/octet-stream"
    
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    
    return Response(content=content, media_type=content_type)
