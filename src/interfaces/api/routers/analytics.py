from fastapi import APIRouter, Depends, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from src.application.services.market_analytics_service import MarketAnalyticsService
from src.application.services.budget_optimizer_service import BudgetOptimizerService
from src.interfaces.api.deps import verify_api_key

router = APIRouter(prefix="/api", tags=["analytics"])

class BudgetOptimizeRequest(BaseModel):
    budget_limit: float = 80.0
    user_id: int = 2
    target_product_ids: Optional[List[int]] = None
    user_location: str = "ES"

@router.get("/analytics/market-index")
async def get_market_index(
    period: str = Query(default="3M", description="1M, 3M, 6M, 1A, ALL"),
    user_id: int = Query(default=2)
):
    """Calcula y devuelve el Índice Bursátil MOTU (EMI) por Waves con serie histórica."""
    return MarketAnalyticsService.get_market_index(period=period, user_id=user_id)

@router.post("/cart/budget-optimize")
async def optimize_cart_budget(request: BudgetOptimizeRequest):
    """Encuentra la combinación matemática óptima de compras dentro de un presupuesto dado."""
    return BudgetOptimizerService.optimize_cart(
        budget_limit=request.budget_limit,
        user_id=request.user_id,
        target_product_ids=request.target_product_ids,
        user_location=request.user_location
    )

@router.get("/sync/delta-updates")
async def get_sync_delta_updates(since: Optional[str] = Query(default=None)):
    """Suministra el catálogo optimizado para caché y búsqueda instantánea en IndexedDB."""
    return MarketAnalyticsService.get_delta_updates(since_timestamp=since)
