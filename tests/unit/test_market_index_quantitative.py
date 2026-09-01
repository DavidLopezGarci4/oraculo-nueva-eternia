import pytest
from src.application.services.market_analytics_service import MarketAnalyticsService

def test_market_index_quantitative_structure():
    data = MarketAnalyticsService.get_market_index(period="3M", user_id=2)
    
    assert "current_index_value" in data
    assert "base_msrp_value" in data
    assert "trend_pct" in data
    assert "trend_direction" in data
    assert "status_label" in data
    assert "historical_series" in data
    assert "waves_breakdown" in data
    
    assert isinstance(data["current_index_value"], float)
    assert isinstance(data["base_msrp_value"], float)
    assert data["relevance_score"] if "relevance_score" in data else True
    assert len(data["historical_series"]) > 0
    assert len(data["waves_breakdown"]) > 0
