import pytest
from unittest.mock import AsyncMock, patch
from src.infrastructure.scrapers.base import ScrapedOffer
from src.application.services.vinted_hunter_service import VintedHunterService
from src.domain.models import ProductModel
from tests.conftest import _TestSession

@pytest.mark.asyncio
async def test_vinted_hunter_detects_bargain(client):
    # 1. Crear producto con P25 = 30.0€
    with _TestSession() as db:
        product = ProductModel(
            name="He-Man Origins",
            sub_category="Origins",
            release_year=2020,
            retail_price=19.99,
            p25_price=30.0,
            is_vintage=False,
            ean="GNN84"
        )
        db.add(product)
        db.commit()

    # 2. Oferta con precio base 12.0€ (Landed: 12 + 5 + 0.24 = 17.24€ < 30.0€) -> Ahorro > 40%
    sample_offer = ScrapedOffer(
        product_name="He-Man Masters of the Universe Origins",
        price=12.0,
        currency="EUR",
        url="https://www.vinted.es/items/123456-he-man-origins",
        shop_name="Vinted",
        is_available=True,
        image_url="https://images.vinted.net/test.jpg"
    )

    with patch("src.application.services.vinted_hunter_service.VintedScraper.search", new_callable=AsyncMock) as mock_search, \
         patch("src.application.services.vinted_hunter_service.ScrapingPipeline.update_database") as mock_pipeline, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_bargain_hunt_alert", new_callable=AsyncMock) as mock_tg_alert:
        
        mock_search.return_value = [sample_offer]

        res = await VintedHunterService.run_hunt(query="auto", chat_id="12345678")
        
        assert res["total_scraped"] == 1
        assert res["bargains_found"] >= 1
        assert mock_tg_alert.called
        
        call_kwargs = mock_tg_alert.call_args.kwargs
        assert call_kwargs["product_name"] == "He-Man Origins"
        assert call_kwargs["price"] == 12.0
        assert call_kwargs["landed_price"] > 12.0
        assert call_kwargs["savings_pct"] > 30.0
