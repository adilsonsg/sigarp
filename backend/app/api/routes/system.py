from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["Sistema"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "status": "online",
    }
