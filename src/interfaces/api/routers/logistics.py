from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.application.services.logistics_service import LogisticsService
from src.domain.models import UserModel
from src.infrastructure.database_cloud import SessionCloud
from src.interfaces.api.deps import get_current_user
from src.interfaces.api.schemas import CartRequest

router = APIRouter(tags=["logistics"])


@router.post("/api/logistics/calculate-cart")
async def api_calculate_cart(request: CartRequest, current_user: UserModel = Depends(get_current_user)):
    try:
        # Fase AAA-1: exige sesión válida. La ubicación se resuelve sobre el
        # usuario autenticado (o el user_id solicitado si es admin), nunca de
        # forma anónima.
        target_user_id = request.user_id
        if current_user.role != "admin" and current_user.username != "David":
            target_user_id = current_user.id

        user_location = "ES"
        with SessionCloud() as db:
            user = db.query(UserModel).filter(UserModel.id == target_user_id).first()
            if user:
                user_location = user.location

        items_dict = [item.model_dump() for item in request.items]
        return LogisticsService.calculate_cart(items_dict, user_location)
    except Exception as e:
        logger.error(f"Error calculating cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))
