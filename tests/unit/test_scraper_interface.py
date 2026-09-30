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
