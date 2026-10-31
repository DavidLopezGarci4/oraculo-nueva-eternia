from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/api/health")
def api_health():
    """Health check para la extensión de Chrome y sondas TecnoRed"""
    return {"status": "ok", "service": "oraculo", "version": settings.VERSION}
