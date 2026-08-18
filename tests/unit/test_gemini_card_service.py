import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.application.services.gemini_card_service import GeminiCardService


@pytest.mark.asyncio
async def test_enhance_card_obrero_norem():
    """Verifica que la generación de óleo box-art estilo Rudy Obrero y Earl Norem devuelva estructura completa."""
    result = await GeminiCardService.enhance_card(
        product_name="He-Man (Battle Armor)",
        sub_category="MOTU Origins",
        style="obrero_norem_80s",
        condition="MOC",
        grading=9.8
    )

    assert result["style"] == "obrero_norem_80s"
    assert "Rudy Obrero" in result["style_name"]
    assert result["lore"] is not None
    assert isinstance(result["stats"], dict)
    assert "fuerza" in result["stats"]
    assert "magia" in result["stats"]
    assert "defensa" in result["stats"]
    assert "agilidad" in result["stats"]
    assert result["special_move"] is not None
    assert result["rarity_class"] is not None


@pytest.mark.asyncio
async def test_enhance_card_alcala_texeira():
    """Verifica el estilo mini-cómic vintage de Alfredo Alcala y Mark Texeira."""
    result = await GeminiCardService.enhance_card(
        product_name="Skeletor",
        sub_category="Vintage 80s",
        style="alcala_texeira_minicomic",
        condition="LOOSE",
        grading=8.5
    )

    assert result["style"] == "alcala_texeira_minicomic"
    assert "Alfredo Alcala" in result["style_name"]
    assert result["lore"] is not None
    assert isinstance(result["stats"], dict)


@pytest.mark.asyncio
async def test_enhance_card_legacy_aliases():
    """Verifica que los estilos antiguos se mapeen correctamente a los estilos de ilustradores."""
    result_oil = await GeminiCardService.enhance_card(
        product_name="Trap Jaw",
        style="oil_vintage"
    )
    assert result_oil["style"] == "obrero_norem_80s"

    result_comic = await GeminiCardService.enhance_card(
        product_name="Tri-Klops",
        style="comic_retro"
    )
    assert result_comic["style"] == "alcala_texeira_minicomic"


@pytest.mark.asyncio
async def test_enhance_card_with_mocked_multimodal_gemini():
    """Verifica la integración con mock de la respuesta multimodal de Gemini Flash Image."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                    }
                }]
            }
        }]
    }

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with patch("src.core.config.settings.GEMINI_API_KEY", "test-key"):
            art = await GeminiCardService._generate_ai_art(
                product_name="Man-At-Arms",
                sub_category="MOTU Origins",
                style="gimenez_santalucia_modern",
                image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            )
            assert art is not None
            assert art.startswith("data:image/png;base64,")

