import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bs4 import BeautifulSoup

from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper
from src.infrastructure.scrapers.wallapop_scraper import WallapopScraper


@pytest.mark.asyncio
async def test_amazon_scraper_zero_cost_cascade():
    """Verifica que AmazonScraper intenta primero curl_cffi directo sin ScraperAPI."""
    scraper = AmazonScraper()
    
    mock_html = """
    <html>
        <body>
            <div data-asin="B09H1V7XYZ">
                <h2><span>He-Man MOTU Origins</span></h2>
                <span class="a-price"><span class="a-offscreen">19,99 €</span></span>
                <a class="a-link-normal" href="/dp/B09H1V7XYZ"></a>
            </div>
        </body>
    </html>
    """
    
    with patch.object(scraper, "_curl_get", new_callable=AsyncMock) as mock_curl:
        mock_curl.return_value = mock_html
        
        offers = await scraper.search("masters of the universe origins")
        
        # Debe haber llamado a _curl_get con use_scraperapi=False
        assert mock_curl.called
        call_kwargs = mock_curl.call_args[1]
        assert call_kwargs.get("use_scraperapi") is False
        assert len(offers) == 1
        assert offers[0].product_name == "He-Man MOTU Origins"
        assert offers[0].price == 19.99
        assert "B09H1V7XYZ" in offers[0].url


@pytest.mark.asyncio
async def test_smythstoys_scraper_zero_cost_cascade():
    """Verifica que SmythsToysScraper parsea correctamente ofertas desde la categoría de MOTU."""
    scraper = SmythsToysScraper()
    
    mock_html = """
    <html>
        <body>
            <div class="product-item">
                <a href="/de/de-de/spielzeug/action-spielzeug/actionfiguren/masters-of-the-universe/p/123456">
                    <span class="title">Masters of the Universe Origins Skeletor</span>
                </a>
                <span class="price">17,99 €</span>
                <img src="https://image.smythstoys.com/123456.jpg" />
            </div>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(mock_html, "html.parser")
    offers = scraper._parse_html(soup, set())
    
    assert len(offers) == 1
    assert "Skeletor" in offers[0].product_name
    assert offers[0].price == 17.99
    assert offers[0].shop_name == "SmythsToys"


@pytest.mark.asyncio
async def test_wallapop_apify_rotation_fallback():
    """Verifica que WallapopScraper rota tokens en Apify cuando recibe 402/429."""
    scraper = WallapopScraper()
    
    with patch("src.infrastructure.scrapers.wallapop_scraper.AsyncSession") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session_cls.return_value.__aenter__.return_value = mock_session
        
        # Token 1 da 402 (agotado), Token 2 da 200 con datos
        resp_402 = MagicMock()
        resp_402.status_code = 402
        
        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = [
            {
                "id": "item123",
                "title": "He-Man Origins MOC",
                "price": 25.0,
                "web_slug": "he-man-origins-item123",
                "images": [{"original": "https://cdn.wallapop.com/img1.jpg"}]
            }
        ]
        
        mock_session.post.side_effect = [resp_402, resp_200]
        
        with patch.dict("os.environ", {"APIFY_TOKEN": "token1", "APIFY_TOKEN2": "token2"}):
            with patch("src.core.config.settings.APIFY_TOKEN", "token1"):
                with patch("src.core.config.settings.APIFY_TOKEN2", "token2"):
                    # Limpiar tokens agotados previos
                    WallapopScraper.global_apify_exhausted_tokens.clear()
                    
                    offers = await scraper.search_via_api("origins", max_items=10)
                    
                    assert len(offers) >= 1
                    assert offers[0].product_name == "He-Man Origins MOC"
                    assert offers[0].price == 25.0
                    assert "token1" in WallapopScraper.global_apify_exhausted_tokens
