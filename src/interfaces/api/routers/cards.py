from fastapi import APIRouter, Depends
from src.interfaces.api.deps import verify_device
from src.interfaces.api.schemas import CardAiEnhanceInput, CardAiEnhanceOutput
from src.application.services.gemini_card_service import GeminiCardService

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.post("/ai-enhance", response_model=CardAiEnhanceOutput, dependencies=[Depends(verify_device)])
async def enhance_card_with_ai(payload: CardAiEnhanceInput):
    """
    Transforma un cromo digital usando la API de Gemini / Imagen 3 para arte retro 80s o lore con stats RPG.
    """
    result = await GeminiCardService.enhance_card(
        product_name=payload.product_name,
        sub_category=payload.sub_category,
        style=payload.style,
        condition=payload.condition,
        grading=payload.grading
    )
    return result
