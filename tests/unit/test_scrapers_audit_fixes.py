from datetime import timedelta, timezone
import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import API_KEY


# ─── 1. Baja completa de DVDStoreSpain ───────────────────────────────────────

def test_dvdstorespain_removed_from_registries_and_telegram():
    from src.interfaces.api.deps import REGISTERED_SPIDERS, CANONICAL_SPIDER_NAMES
    import src.application.jobs.daily_scan as daily_scan
    from src.infrastructure.services.telegram_listener import TelegramListener

    assert "DVDStoreSpain" not in REGISTERED_SPIDERS
    assert all("dvdstore" not in s.lower() for s in REGISTERED_SPIDERS)
    assert "dvdstorespain" not in CANONICAL_SPIDER_NAMES
    assert not hasattr(daily_scan, "DVDStoreSpainScraper")

    src_text = inspect.getsource(TelegramListener.cmd_run)
    assert "dvdstorespain" not in src_text.lower()


def test_dvdstorespain_excluded_from_status_and_rejected_on_run(client):
    from src.domain.models import ScraperStatusModel
    from src.interfaces.api.routers.scrapers import SessionCloud

    headers = {"X-API-Key": API_KEY}
    try:
        with SessionCloud() as db:
            db.add(ScraperStatusModel(spider_name="DVDStoreSpain", status="completed"))
            db.add(ScraperStatusModel(spider_name="dvdstorespain", status="stopped"))
            db.commit()

        status_resp = client.get("/api/scrapers/status", headers=headers)
        assert status_resp.status_code == 200, status_resp.text
        names = {s["spider_name"].lower() for s in status_resp.json()}
        assert "dvdstorespain" not in names

        for candidate in ("DVDStoreSpain", "dvdstorespain"):
            run_resp = client.post(
                "/api/scrapers/run",
                json={"spider_name": candidate},
                headers=headers,
            )
            assert run_resp.status_code == 400
    finally:
        with SessionCloud() as db:
            db.query(ScraperStatusModel).filter(
                ScraperStatusModel.spider_name.in_(["DVDStoreSpain", "dvdstorespain"])
            ).delete(synchronize_session=False)
            db.commit()


# ─── 2. BaseScraper: Coherencia TLS/Headers y Detección de Bloqueos ───────────

def test_base_scraper_headers_aligned_with_curl_impersonate():
    from src.infrastructure.scrapers.base import BaseScraper

    class DummyScraper(BaseScraper):
        async def search(self, query: str = "auto"):
            return []

    sig = inspect.signature(BaseScraper._curl_get)
    assert sig.parameters["impersonate"].default == "chrome124"

    scraper = DummyScraper(shop_name="Dummy", base_url="https://example.com")
    headers = scraper._get_random_header()
    assert "Chrome/124.0.0.0" in headers["User-Agent"]
    assert 'v="124"' in headers["sec-ch-ua"]


def test_base_scraper_detect_block_identifies_cloudflare_and_ebay_captcha():
    from src.infrastructure.scrapers.base import BaseScraper

    class DummyScraper(BaseScraper):
        async def search(self, query: str = "auto"):
            return []

    logs = []
    scraper = DummyScraper(shop_name="Dummy", base_url="https://example.com")
    scraper.log_callback = logs.append

    cf_html = '<!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title></head><body>cf-chl</body></html>'
    assert scraper._detect_block(cf_html) is True
    assert any("Cloudflare" in m for m in logs)

    logs.clear()
    ebay_html = '<html><body><h1>Pardon Our Interruption...</h1><form action="/splashui/captcha"></form></body></html>'
    assert scraper._detect_block(ebay_html) is True
    assert any("eBay" in m or "CAPTCHA" in m for m in logs)


# ─── 3. FantasiaScraper: Fail-Fast ante Cloudflare y Estado Blocked ───────────

@pytest.mark.asyncio
async def test_fantasia_fail_fast_when_blocked_skips_known_urls_and_playwright():
    from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper

    scraper = FantasiaScraper()
    logs = []
    scraper.log_callback = logs.append

    async def fake_curl_get(url, **kwargs):
        scraper.blocked = True
        return None

    with patch.object(scraper, "_curl_get", side_effect=fake_curl_get) as mock_curl, \
         patch.object(scraper, "_search_playwright", new_callable=AsyncMock) as mock_pw:
        offers = await scraper.search("auto")

    assert offers == []
    assert scraper.blocked is True
    assert mock_curl.call_count == 1
    assert mock_pw.call_count == 0
    assert any("Fantasia Personajes" in m or "Bloqueo" in m for m in logs)


@pytest.mark.asyncio
async def test_fantasia_blocks_vintage_query():
    from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper

    scraper = FantasiaScraper()
    with patch.object(scraper, "_curl_get", new_callable=AsyncMock) as mock_curl:
        offers = await scraper.search("he-man vintage 1984")

    assert offers == []
    assert mock_curl.call_count == 0


def test_run_scraper_task_marks_blocked_status_when_single_spider_blocked(client):
    from src.domain.models import ScraperStatusModel, ScraperExecutionLogModel
    from src.interfaces.api.routers.scrapers import SessionCloud, run_scraper_task

    with SessionCloud() as db:
        st = db.query(ScraperStatusModel).filter(
            ScraperStatusModel.spider_name == "Fantasia Personajes"
        ).first()
        if not st:
            st = ScraperStatusModel(spider_name="Fantasia Personajes", status="stopped")
            db.add(st)
        log = ScraperExecutionLogModel(
            spider_name="Fantasia Personajes",
            status="running",
            trigger_type="manual",
            logs="",
        )
        db.add(log)
        db.commit()
        log_id = log.id

    fake_spider = MagicMock()
    fake_spider.shop_name = "Fantasia Personajes"
    fake_spider.spider_name = "fantasia personajes"
    fake_spider.blocked = True
    fake_spider.search = AsyncMock(return_value=[])

    with patch("src.infrastructure.scrapers.fantasia_scraper.FantasiaScraper", return_value=fake_spider), \
         patch("src.infrastructure.scrapers.pipeline.ScrapingPipeline.update_database", return_value=0), \
         patch("src.interfaces.api.routers.scrapers._get_madrid_tz", return_value=timezone.utc):
        run_scraper_task("Fantasia Personajes", trigger_type="manual", log_id=log_id)

    with SessionCloud() as db:
        st = db.query(ScraperStatusModel).filter(
            ScraperStatusModel.spider_name == "Fantasia Personajes"
        ).first()
        log = db.query(ScraperExecutionLogModel).filter(
            ScraperExecutionLogModel.id == log_id
        ).first()
        assert st.status == "blocked"
        assert log.status == "blocked"


def test_get_madrid_tz_falls_back_to_utc_plus_1_on_tzdata_oserror():
    from src.interfaces.api.routers import scrapers as scrapers_router

    prev_cached = scrapers_router._CACHED_MADRID_TZ
    try:
        scrapers_router._CACHED_MADRID_TZ = None
        with patch.object(scrapers_router, "ZoneInfo", side_effect=OSError(22, "Invalid argument")):
            tz = scrapers_router._get_madrid_tz()
        assert tz == timezone(timedelta(hours=1))
    finally:
        scrapers_router._CACHED_MADRID_TZ = prev_cached


# ─── 4. EbayScraper: Parser .s-card, Tildes Españolas y Bloqueo Playwright ────

def test_ebay_html_parser_handles_s_card_links_spanish_accents_and_vintage():
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper

    scraper = EbayScraper()
    html = """
    <ul>
      <li class="s-card">
        <a href="https://www.ebay.es/usr/seller123">Vendedor</a>
        <div class="s-card__title">Masters del Universo Orígenes Skeletor Mattel Nuevo</div>
        <span class="s-card__price">24,95 EUR</span>
        <a class="s-card__link" href="https://www.ebay.es/itm/123456789012?hash=abc">Ver</a>
      </li>
      <li class="s-card">
        <a href="https://www.ebay.es/b/watch">Seguir</a>
        <div class="s-card__title">Masters del Universo Origenes He-Man Cartoon Collection</div>
        <span class="s-card__price">22,00 EUR</span>
        <a href="/itm/987654321098?itmmeta=xyz">Relativo</a>
      </li>
      <li class="s-card">
        <div class="s-card__title">Shop on eBay</div>
        <span class="s-card__price">1,00 EUR</span>
        <a class="s-card__link" href="https://www.ebay.es/itm/123456">Dummy</a>
      </li>
      <li class="s-card">
        <div class="s-card__title">He-Man Vintage 1982 Masters of the Universe</div>
        <span class="s-card__price">95,00 EUR</span>
        <a class="s-card__link" href="https://www.ebay.es/itm/555666777888">Vintage</a>
      </li>
    </ul>
    """
    offers = scraper._parse_ebay_html(html, "masters del universo origenes")
    assert len(offers) == 2
    assert offers[0].url == "https://www.ebay.es/itm/123456789012"
    assert offers[1].url == "https://www.ebay.es/itm/987654321098"


@pytest.mark.asyncio
async def test_ebay_playwright_extract_page_items_and_captcha_block():
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper

    scraper = EbayScraper()
    page = AsyncMock()
    page.content = AsyncMock(return_value="""
    <ul>
      <li class="s-card">
        <a href="https://www.ebay.es/usr/vendedor">Perfil</a>
        <div class="s-card__title">Masters del Universo Orígenes Man-At-Arms</div>
        <span class="s-card__price">19,99 €</span>
        <a href="https://www.ebay.es/itm/333444555666?foo=bar">Producto</a>
      </li>
    </ul>
    """)
    offers = await scraper._extract_page_items(page, "masters del universo origenes")
    assert len(offers) == 1
    assert offers[0].url == "https://www.ebay.es/itm/333444555666"

    # Ahora probar detección de bloqueo cuando curl da 403 y Playwright cae en /splashui/captcha
    scraper_blocked = EbayScraper()
    mock_session = AsyncMock()
    resp_403 = MagicMock(status_code=403, text="Forbidden")
    mock_session.get = AsyncMock(return_value=resp_403)
    mock_session.close = AsyncMock()

    mock_pw_page = AsyncMock()
    mock_pw_resp = MagicMock(status=200)
    mock_pw_page.goto = AsyncMock(return_value=mock_pw_resp)
    mock_pw_page.url = "https://www.ebay.es/splashui/captcha?ap=1"
    mock_pw_page.content = AsyncMock(return_value="<html><body>Pardon Our Interruption</body></html>")

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_pw_page)
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_pw = MagicMock()
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_pw_cm = MagicMock()
    mock_pw_cm.__aenter__ = AsyncMock(return_value=mock_pw)
    mock_pw_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("curl_cffi.requests.AsyncSession", return_value=mock_session), \
         patch("playwright.async_api.async_playwright", return_value=mock_pw_cm), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        res = await scraper_blocked.search("auto")

    assert res == []
    assert scraper_blocked.blocked is True
    assert mock_pw_page.goto.call_count == 1


# ─── 5. BixotoScraper: Multi-Query Auto, .product-card y Guardas ─────────────

@pytest.mark.asyncio
async def test_bixoto_auto_queries_card_variants_and_vintage_guard():
    from src.infrastructure.scrapers.bixoto_scraper import BixotoScraper

    scraper = BixotoScraper()
    called_urls = []

    html_q1 = """
    <html><body>
      <div class="product-card">
        <div class="product-card__top">
          <a href="/es/p/mattel-motu-origins-skeletor-123">
            <img src="https://cdn.bixoto.com/skeletor.jpg" />
            <div class="product-card__name">Mattel Masters of the Universe Origins Skeletor</div>
          </a>
        </div>
        <div class="product-card__bottom">
          <div class="price"><span class="special">18,99 €</span></div>
        </div>
      </div>
      <div class="product-card__top">
        <a href="/es/p/mattel-motu-vintage-1982">
          <div class="product-card__name">He-Man Vintage 1982</div>
        </a>
        <div class="price">99,00 €</div>
      </div>
      <script>slug:"mattel-motu-origins-skeletor-123",ean13s:["0194735049103"]</script>
    </body></html>
    """
    html_q2 = """
    <html><body>
      <div class="product-card">
        <div class="product-card__top">
          <a href="/es/p/mattel-motu-origins-skeletor-123">
            <div class="product-card__name">Mattel Masters of the Universe Origins Skeletor</div>
          </a>
        </div>
        <div class="product-card__bottom">
          <div class="price">18,99 €</div>
        </div>
      </div>
      <div class="product-card">
        <div class="product-card__top">
          <a href="/es/p/mattel-masters-del-universo-he-man-456">
            <div class="product-card__name">Mattel Masters del Universo He-Man</div>
          </a>
        </div>
        <div class="product-card__bottom">
          <div class="price"><span class="original">21,50 €</span></div>
        </div>
      </div>
      <script>slug:"mattel-masters-del-universo-he-man-456",ean13s:["0194735111222"]</script>
    </body></html>
    """
    html_q3 = "<html><body><div>Sin resultados</div></body></html>"

    async def fake_curl(url, **kwargs):
        called_urls.append(url)
        if len(called_urls) == 1:
            return html_q1
        if len(called_urls) == 2:
            return html_q2
        return html_q3

    with patch.object(scraper, "_curl_get", side_effect=fake_curl), \
         patch.object(scraper, "_random_sleep", new_callable=AsyncMock):
        offers = await scraper.search("auto")

    assert len(called_urls) == 3
    assert len(offers) == 2
    urls = {o.url for o in offers}
    assert "https://bixoto.com/es/p/mattel-motu-origins-skeletor-123" in urls
    assert "https://bixoto.com/es/p/mattel-masters-del-universo-he-man-456" in urls
    eans = {o.ean for o in offers}
    assert "0194735049103" in eans
    assert "0194735111222" in eans


@pytest.mark.asyncio
async def test_bixoto_does_not_call_urllib_when_blocked():
    from src.infrastructure.scrapers.bixoto_scraper import BixotoScraper

    scraper = BixotoScraper()

    async def fake_curl(url, **kwargs):
        scraper.blocked = True
        return None

    with patch.object(scraper, "_curl_get", side_effect=fake_curl), \
         patch("urllib.request.urlopen") as mock_urlopen:
        offers = await scraper.search("auto")

    assert offers == []
    assert scraper.blocked is True
    assert mock_urlopen.call_count == 0
