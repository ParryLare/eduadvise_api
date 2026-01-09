"""
Application startup script.

This script provides an easy way to run the application with proper configuration.
"""
import uvicorn
import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))


def main():
    """Run the FastAPI application."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
