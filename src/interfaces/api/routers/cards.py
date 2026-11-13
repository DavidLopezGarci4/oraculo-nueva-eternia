from fastapi import APIRouter, Depends
from src.core.rate_limit import rate_limit
from src.domain.models import UserModel
from src.interfaces.api.deps import get_current_user
from src.interfaces.api.schemas import CardAiEnhanceInput, CardAiEnhanceOutput
from src.application.services.gemini_card_service import GeminiCardService

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.post(
    "/ai-enhance",
    response_model=CardAiEnhanceOutput,
    dependencies=[Depends(rate_limit(10, 300, "cards-ai-enhance"))],
)
async def enhance_card_with_ai(
    payload: CardAiEnhanceInput,
    _current_user: UserModel = Depends(get_current_user),
):
    """
    Transforma un cromo digital usando la API de Gemini / Imagen 3 para arte retro 80s o lore con stats RPG.
    """
    result = await GeminiCardService.enhance_card(
        product_name=payload.product_name,
        sub_category=payload.sub_category,
        style=payload.style,
        condition=payload.condition,
        grading=payload.grading,
        image_url=payload.image_url,
        image_base64=payload.image_base64
    )
    return result
