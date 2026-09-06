from fastapi import APIRouter
from datetime import datetime, timezone
from ...config import settings

router = APIRouter()


@router.get("/health")
async def get_health():
    """System diagnostic and health check."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "production_helpline": settings.PRODUCTION_HELPLINE_NUMBER,
        "providers": {
            "telephony": settings.TELEPHONY_PROVIDER,
            "stt": "sarvam" if settings.SARVAM_API_KEY else "mock",
            "tts": "sarvam" if settings.SARVAM_API_KEY else "mock",
            "llm": "gemini" if settings.GEMINI_API_KEY else "mock"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
