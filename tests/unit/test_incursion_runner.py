import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from scripts.run_single_incursion import get_scraper_class, SUPPORTED_SCRAPERS, execute_scraper

def test_supported_scrapers_list():
    assert len(SUPPORTED_SCRAPERS) == 6
    expected = ["SmythsToys", "Wallapop", "Vinted", "Ebay", "Amazon", "BBTS"]
    assert SUPPORTED_SCRAPERS == expected

def test_get_scraper_class():
    for name in SUPPORTED_SCRAPERS:
        cls = get_scraper_class(name)
        assert cls is not None

    assert get_scraper_class("UnknownStore") is None

@pytest.mark.asyncio
async def test_execute_scraper_success():
    mock_scraper = MagicMock()
    mock_scraper.shop_name = "MockShop"
    mock_offer = MagicMock()
    mock_offer.product_name = "He-Man Origins"
    mock_offer.price = 19.99
    mock_offer.currency = "EUR"
    mock_offer.is_available = True
    mock_offer.url = "http://example.com"
    mock_scraper.search = AsyncMock(return_value=[mock_offer])

    with patch("scripts.run_single_incursion.get_scraper_class", return_value=lambda: mock_scraper):
        with patch("src.infrastructure.scrapers.pipeline.ScrapingPipeline.update_database", return_value=1):
            result = await execute_scraper("MockShop", "auto", persist=True)
            assert result["status"] == "OK"
            assert result["found"] == 1
            assert result["saved"] == 1

@pytest.mark.asyncio
async def test_execute_scraper_failure_resilience():
    mock_scraper = MagicMock()
    mock_scraper.search = AsyncMock(side_effect=RuntimeError("Connection timeout"))

    with patch("scripts.run_single_incursion.get_scraper_class", return_value=lambda: mock_scraper):
        result = await execute_scraper("MockShop", "auto", persist=False)
        assert "Error" in result["status"]
        assert result["found"] == 0
        assert result["saved"] == 0
