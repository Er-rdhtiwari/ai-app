from fastapi import APIRouter, Response
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes.
    Returns 200 OK with status information.
    """
    logger.debug("Health check requested")
    return {
        "status": "ok",
        "service": "ai-app-backend"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    Can be extended to check dependencies (database, external APIs, etc.)
    """
    # Add checks for dependencies here if needed
    # For now, always return ready
    return {
        "status": "ready",
        "checks": {
            "api": "ok"
        }
    }

# Made with Bob
