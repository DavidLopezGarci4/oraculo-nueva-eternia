import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from src.infrastructure.scrapers.base import ScrapedOffer
from src.application.services.vinted_hunter_service import VintedHunterService
from src.domain.models import ProductModel, HunterAlertLogModel, BlackcludedItemModel, PendingMatchModel
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
         patch("src.application.services.vinted_hunter_service.telegram_service.send_bargain_hunt_alert", new_callable=AsyncMock) as mock_tg_alert, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_message", new_callable=AsyncMock):
        
        mock_search.return_value = [sample_offer]

        res = await VintedHunterService.run_hunt(query="auto", chat_id="12345678")
        
        assert res["total_scraped"] == 1
        assert res["bargains_found"] == 1
        assert mock_tg_alert.called
        
        call_kwargs = mock_tg_alert.call_args.kwargs
        assert call_kwargs["product_name"] == "He-Man Origins"
        assert call_kwargs["price"] == 12.0
        assert call_kwargs["landed_price"] > 12.0
        assert call_kwargs["benchmark_price"] == 19.99
        assert call_kwargs["savings_pct"] > 10.0

@pytest.mark.asyncio
async def test_vinted_hunter_discards_parts_and_damage(client):
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

    sample_offer_despiece = ScrapedOffer(
        product_name="He-Man Masters of the Universe Origins despiece incompleto",
        price=10.0,
        currency="EUR",
        url="https://www.vinted.es/items/111-despiece",
        shop_name="Vinted",
        is_available=True,
        image_url="https://images.vinted.net/test.jpg"
    )

    with patch("src.application.services.vinted_hunter_service.VintedScraper.search", new_callable=AsyncMock) as mock_search, \
         patch("src.application.services.vinted_hunter_service.ScrapingPipeline.update_database") as mock_pipeline, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_bargain_hunt_alert", new_callable=AsyncMock) as mock_tg_alert, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_message", new_callable=AsyncMock):
        
        mock_search.return_value = [sample_offer_despiece]

        res = await VintedHunterService.run_hunt(query="auto", chat_id="12345678")
        
        # Descartado por keyword "despiece"
        assert res["total_scraped"] == 1
        assert res["bargains_found"] == 0
        assert not mock_tg_alert.called

@pytest.mark.asyncio
async def test_vinted_hunter_discards_sub_nine_euro_floor(client):
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

    sample_offer_junk = ScrapedOffer(
        product_name="He-Man Origins",
        price=4.50, # Sub 9€ floor
        currency="EUR",
        url="https://www.vinted.es/items/222-cheap",
        shop_name="Vinted",
        is_available=True,
        image_url="https://images.vinted.net/test.jpg"
    )

    with patch("src.application.services.vinted_hunter_service.VintedScraper.search", new_callable=AsyncMock) as mock_search, \
         patch("src.application.services.vinted_hunter_service.ScrapingPipeline.update_database") as mock_pipeline, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_bargain_hunt_alert", new_callable=AsyncMock) as mock_tg_alert, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_message", new_callable=AsyncMock):
        
        mock_search.return_value = [sample_offer_junk]

        res = await VintedHunterService.run_hunt(query="auto", chat_id="12345678")
        
        # Descartado por precio suelo (<9€)
        assert res["total_scraped"] == 1
        assert res["bargains_found"] == 0
        assert not mock_tg_alert.called

@pytest.mark.asyncio
async def test_vinted_hunter_deduplicates_same_day(client):
    url_test = "https://www.vinted.es/items/999999-skeletor-origins"
    
    # 1. Registrar producto y registrar que ya se alertó hoy
    with _TestSession() as db:
        product = ProductModel(
            name="Skeletor Origins",
            sub_category="Origins",
            release_year=2020,
            retail_price=19.99,
            p25_price=35.0,
            is_vintage=False,
            ean="GNN85"
        )
        db.add(product)
        # Añadir a hunter_alert_logs con fecha de hoy
        db.add(HunterAlertLogModel(
            url=url_test,
            product_name="Skeletor Origins",
            price=10.0,
            sent_at=datetime.now(timezone.utc)
        ))
        db.commit()

    sample_offer = ScrapedOffer(
        product_name="Skeletor Masters of the Universe Origins",
        price=10.0,
        currency="EUR",
        url=url_test,
        shop_name="Vinted",
        is_available=True,
        image_url="https://images.vinted.net/test2.jpg"
    )

    with patch("src.application.services.vinted_hunter_service.VintedScraper.search", new_callable=AsyncMock) as mock_search, \
         patch("src.application.services.vinted_hunter_service.ScrapingPipeline.update_database") as mock_pipeline, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_bargain_hunt_alert", new_callable=AsyncMock) as mock_tg_alert, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_message", new_callable=AsyncMock):
        
        mock_search.return_value = [sample_offer]

        res = await VintedHunterService.run_hunt(query="auto", chat_id="12345678")
        
        # Debe detectarlo como recurrente y NO enviar alerta push
        assert res["total_scraped"] == 1
        assert res["bargains_found"] == 0
        assert res["recurring_bargains"] == 1
        assert not mock_tg_alert.called

@pytest.mark.asyncio
async def test_vinted_hunter_skips_discarded_offers(client):
    url_discarded = "https://www.vinted.es/items/888888-discarded-item"
    
    # 1. Registrar como descartado en BlackcludedItemModel
    with _TestSession() as db:
        product = ProductModel(
            name="Teela Origins",
            sub_category="Origins",
            release_year=2020,
            retail_price=19.99,
            p25_price=30.0,
            is_vintage=False,
            ean="GNN86"
        )
        db.add(product)
        db.add(BlackcludedItemModel(
            url=url_discarded,
            scraped_name="Teela Origins fake",
            reason="Descartado por usuario"
        ))
        db.commit()

    sample_offer = ScrapedOffer(
        product_name="Teela Masters of the Universe Origins",
        price=10.0,
        currency="EUR",
        url=url_discarded,
        shop_name="Vinted",
        is_available=True,
        image_url="https://images.vinted.net/test3.jpg"
    )

    with patch("src.application.services.vinted_hunter_service.VintedScraper.search", new_callable=AsyncMock) as mock_search, \
         patch("src.application.services.vinted_hunter_service.ScrapingPipeline.update_database") as mock_pipeline, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_bargain_hunt_alert", new_callable=AsyncMock) as mock_tg_alert, \
         patch("src.application.services.vinted_hunter_service.telegram_service.send_message", new_callable=AsyncMock):
        
        mock_search.return_value = [sample_offer]

        res = await VintedHunterService.run_hunt(query="auto", chat_id="12345678")
        
        # Totalmente omitido
        assert res["total_scraped"] == 1
        assert res["bargains_found"] == 0
        assert res["recurring_bargains"] == 0
        assert not mock_tg_alert.called

