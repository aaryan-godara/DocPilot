"""
AskMyBook — Health Check Endpoint

Provides a simple health check for monitoring and uptime verification.
"""

from fastapi import APIRouter

from app.backend.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns the service status and current version.
    Useful for monitoring, load balancer checks, and CI/CD pipelines.
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "service": settings.app_name,
    }
