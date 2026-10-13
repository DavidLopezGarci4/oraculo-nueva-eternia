import pytest
import importlib

def test_scraper_interface_imports():
    from src.infrastructure.scrapers.interface import ScraperPlugin, ScrapedOffer, ProductOffer
    assert ScraperPlugin is not None
    assert ScrapedOffer is not None
    assert ProductOffer is ScrapedOffer

def test_models_product_offer_alias():
    from src.domain.models import ProductOffer, OfferModel
    assert ProductOffer is OfferModel

def test_scrape_multi_via_cdp_module_loads():
    mod = importlib.import_module("scripts.scrape_multi_via_cdp")
    assert hasattr(mod, "main")
    assert hasattr(mod, "find_chrome_executable")
    assert hasattr(mod, "ensure_chrome_debug_running")
    assert hasattr(mod, "STORE_DEFAULT_URLS")
    assert len(mod.STORE_DEFAULT_URLS) >= 4

def test_scrape_multi_via_cdp_inner_imports():
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper
    from src.infrastructure.scrapers.bbts_scraper import BigBadToyStoreScraper
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline
    from src.infrastructure.scrapers.base import ScrapedOffer
    assert ScrapedOffer is not None


def test_wallapop_manual_scraper_full_families_non_vintage():
    from src.infrastructure.scrapers.wallapop_manual_scraper import WallapopManualScraper
    casual = WallapopManualScraper.FULL_FAMILIES["2. Vendedores Casuales / Chollos"]
    lots = WallapopManualScraper.FULL_FAMILIES["5. Lotes y Liquidaciones"]
    for q in casual + lots:
        assert "origins" in q.lower(), f"Query '{q}' must include 'origins' per Rule 2"


def test_unified_spider_registry_consistency():
    from src.interfaces.api.deps import REGISTERED_SPIDERS, CANONICAL_SPIDER_NAMES
    import src.application.jobs.daily_scan as daily_scan
    assert "ToymiEU" in REGISTERED_SPIDERS
    assert "Bixoto" in REGISTERED_SPIDERS
    assert "DVDStoreSpain" in REGISTERED_SPIDERS
    assert CANONICAL_SPIDER_NAMES["toymieu"] == "ToymiEU"
    assert CANONICAL_SPIDER_NAMES["bixoto"] == "Bixoto"
    assert CANONICAL_SPIDER_NAMES["dvdstorespain"] == "DVDStoreSpain"
    assert hasattr(daily_scan, "DVDStoreSpainScraper")


@pytest.mark.asyncio
async def test_wallapop_import_skips_vintage_items():
    from unittest.mock import patch, MagicMock
    from src.interfaces.api.routers.users import import_wallapop_products
    from src.interfaces.api.schemas import WallapopImportRequest

    req = WallapopImportRequest(products=[
        {
            "title": "He-Man Vintage 1982 Masters of the Universe",
            "price": 45.0,
            "url": "https://es.wallapop.com/item/he-man-1982",
            "imageUrl": "https://img/1.jpg"
        },
        {
            "title": "He-Man Origins Mattel",
            "price": 18.0,
            "url": "https://es.wallapop.com/item/he-man-origins",
            "imageUrl": "https://img/2.jpg"
        },
    ])

    with patch("src.interfaces.api.routers.users.SessionCloud") as mock_sess_cls, \
         patch("src.infrastructure.scrapers.pipeline.clean_purgatory_globally"):
        mock_db = MagicMock()
        mock_sess_cls.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = []

        res = await import_wallapop_products(req)
        assert res["imported"] == 1
        assert res["skipped_irrelevant"] == 1


def test_sync_availability_preserves_vintage_offers():
    from unittest.mock import patch, MagicMock
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline

    vintage_offer = MagicMock()
    vintage_offer.is_vintage = False
    vintage_offer.is_available = True
    vintage_offer.shop_name = "Vinted"
    vintage_offer.url = "https://vinted.es/items/vintage-skeletor"
    vintage_offer.product = MagicMock(is_vintage=True, name="Skeletor Vintage")

    origins_offer = MagicMock()
    origins_offer.is_vintage = False
    origins_offer.is_available = True
    origins_offer.shop_name = "Vinted"
    origins_offer.url = "https://vinted.es/items/origins-skeletor"
    origins_offer.product = MagicMock(is_vintage=False, name="Skeletor Origins")
    origins_offer.last_seen = None
    origins_offer.price = 15.0

    pipeline = ScrapingPipeline([])
    with patch("src.infrastructure.scrapers.pipeline.SessionCloud") as mock_sess_cls:
        mock_db = MagicMock()
        mock_sess_cls.return_value = mock_db
        mock_db.query.return_value.filter.return_value.all.return_value = [vintage_offer, origins_offer]

        pipeline.sync_availability(found_urls=[], shop_names=["Vinted"])
        assert vintage_offer.is_available is True
        assert origins_offer.is_available is False

