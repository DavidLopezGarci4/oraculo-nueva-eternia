import pytest
from unittest.mock import patch, MagicMock
from src.application.services.market_analytics_service import MarketAnalyticsService
from src.domain.models import ProductModel

def test_market_index_calculation():
    """Prueba que el índice bursátil MOTU computa medias por waves y tendencia."""
    with patch("src.application.services.market_analytics_service.SessionCloud") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        p1 = ProductModel(id=1, name="He-Man", sub_category="Origins Wave 1", retail_price=19.99, p25_price=28.0, is_vintage=False)
        p2 = ProductModel(id=2, name="Skeletor", sub_category="Origins Wave 1", retail_price=19.99, p25_price=26.0, is_vintage=False)
        p3 = ProductModel(id=3, name="Trap Jaw", sub_category="Origins Wave 2", retail_price=19.99, p25_price=35.0, is_vintage=False)

        q = MagicMock()
        q.filter.return_value.all.return_value = [p1, p2, p3]
        q.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = q

        res = MarketAnalyticsService.get_market_index(period="3M")

        assert res["current_index_value"] > 20.0
        assert res["trend_direction"] in ["bullish", "bearish", "stable"]
        assert len(res["waves_breakdown"]) >= 2
        assert len(res["historical_series"]) > 0

def test_delta_updates_catalog():
    """Prueba que delta updates entrega el formato correcto de catálogo."""
    with patch("src.application.services.market_analytics_service.SessionCloud") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        p1 = ProductModel(id=1, name="He-Man", sub_category="Origins", retail_price=19.99, p25_price=24.0, is_vintage=False)
        mock_db.query.return_value.filter.return_value.all.return_value = [p1]

        res = MarketAnalyticsService.get_delta_updates(since_timestamp="2026-08-01T00:00:00Z")
        assert res["total_count"] == 1
        assert res["products"][0]["name"] == "He-Man"
        assert "server_time" in res
