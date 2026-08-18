import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.application.services.telegram_oracle_ai import OracleAssistantAI

@pytest.mark.asyncio
async def test_telegram_oracle_ai_collection_query():
    """Prueba la respuesta semántica local sobre valor de la colección."""
    with patch.object(
        OracleAssistantAI,
        "_tool_collection_summary",
        return_value={
            "total_items": 12,
            "total_invested": 220.0,
            "market_value": 310.0,
            "profit": 90.0,
            "roi_pct": 40.9,
            "moc_count": 8,
            "loose_count": 4
        }
    ):
        reply = await OracleAssistantAI.process_user_query("¿Cuánto vale mi colección de figuras?", user_id=2)
        assert "La Fortaleza" in reply
        assert "310.00 €" in reply
        assert "+90.00 €" in reply

@pytest.mark.asyncio
async def test_telegram_oracle_ai_deals_query():
    """Prueba la respuesta semántica local sobre chollos y ofertas."""
    with patch.object(
        OracleAssistantAI,
        "_tool_top_opportunities",
        return_value={
            "deals": [{
                "name": "He-Man Origins",
                "price": 14.50,
                "landed_price": 19.50,
                "shop": "Vinted",
                "url": "https://vinted.es/test",
                "savings_pct": 30.0
            }]
        }
    ):
        reply = await OracleAssistantAI.process_user_query("muéstrame las mejores ofertas y chollos", user_id=2)
        assert "He-Man Origins" in reply
        assert "14.50€" in reply
        assert "Vinted" in reply
