"""Health check endpoint (BRD Section 13: GET /api/health)."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health_check() -> dict:
    """Simple liveness probe for verifying the backend is running."""
    return {"status": "ok", "service": "ai-crm-hcp-backend"}
