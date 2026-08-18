import pytest
from unittest.mock import patch, AsyncMock
from src.application.services.gemini_card_service import GeminiCardService


@pytest.mark.asyncio
async def test_enhance_card_rpg_lore():
    """Verifica que la generación de lore y stats devuelva estructura completa."""
    result = await GeminiCardService.enhance_card(
        product_name="He-Man (Battle Armor)",
        sub_category="MOTU Origins",
        style="rpg_lore",
        condition="MOC",
        grading=9.8
    )

    assert result["style"] == "rpg_lore"
    assert "Ficha de Lore" in result["style_name"]
    assert result["lore"] is not None
    assert isinstance(result["stats"], dict)
    assert "fuerza" in result["stats"]
    assert "magia" in result["stats"]
    assert "defensa" in result["stats"]
    assert "agilidad" in result["stats"]
    assert result["special_move"] is not None
    assert result["rarity_class"] is not None


@pytest.mark.asyncio
async def test_enhance_card_oil_vintage():
    """Verifica la configuración del estilo al óleo vintage."""
    result = await GeminiCardService.enhance_card(
        product_name="Skeletor",
        sub_category="Vintage 80s",
        style="oil_vintage",
        condition="LOOSE",
        grading=8.5
    )

    assert result["style"] == "oil_vintage"
    assert "Óleo Vintage" in result["style_name"]
    assert result["lore"] is not None
    assert isinstance(result["stats"], dict)


@pytest.mark.asyncio
async def test_enhance_card_with_mocked_imagen():
    """Verifica la integración con mock de la respuesta de Imagen 3."""
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "predictions": [
            {"bytesBase64Encoded": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}
        ]
    }

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with patch("src.core.config.settings.GEMINI_API_KEY", "test-key"):
            art = await GeminiCardService._generate_ai_art("Man-At-Arms", "MOTU Origins", "oil_vintage")
            assert art is not None
            assert art.startswith("data:image/png;base64,")
