from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
def api_health():
    """Health check para la extensión de Chrome"""
    return {"status": "ok", "service": "oraculo", "version": "1.0.0"}
