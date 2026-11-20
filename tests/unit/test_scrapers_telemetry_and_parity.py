"""
WU2 RED -> GREEN tests: Per-page & total telemetry across all 17 active scrapers,
BaseScraper._log prefixing & _safe_navigate page detection, SmythsToys ScraperAPI
blocked parity, sync_availability protection in App "all", and daily_scan parity.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import re
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer


class _DummyScraper(BaseScraper):
    async def search(self, query: str = "auto"):
        return []


def _make_fake_playwright(pages_html: list[str]):
    """Builds a minimal async_playwright() mock returning sequential HTML pages."""
    call_idx = {"i": 0}

    class _FakeLocator:
        async def is_visible(self, timeout=0):
            return False

        async def click(self):
            return None

    class _FakeKeyboard:
        async def press(self, key):
            return None

        async def type(self, ch):
            return None

    class _FakeMouse:
        async def wheel(self, x, y):
            return None

        async def move(self, x, y):
            return None

    class _FakePage:
        def __init__(self):
            self.url = "https://example.com"
            self.keyboard = _FakeKeyboard()
            self.mouse = _FakeMouse()
            self._html = pages_html[0] if pages_html else "<html></html>"

        async def goto(self, url, wait_until="domcontentloaded", timeout=60000):
            self.url = url
            idx = min(call_idx["i"], len(pages_html) - 1)
            self._html = pages_html[idx]
            call_idx["i"] += 1
            return SimpleNamespace(status=200)

        async def content(self):
            return self._html

        async def wait_for_selector(self, selector, timeout=10000):
            return None

        async def query_selector(self, selector):
            return None

        async def query_selector_all(self, selector):
            return []

        async def wait_for_timeout(self, ms):
            return None

        def locator(self, selector):
            return _FakeLocator()

        async def add_init_script(self, script):
            return None

        async def close(self):
            return None

    class _FakeContext:
        async def new_page(self):
            return _FakePage()

        async def add_init_script(self, script):
            return None

        async def set_extra_http_headers(self, headers):
            return None

        async def close(self):
            return None

    class _FakeBrowser:
        async def new_context(self, **kwargs):
            return _FakeContext()

        async def close(self):
            return None

    class _FakeChromium:
        async def launch(self, **kwargs):
            return _FakeBrowser()

    class _FakePW:
        def __init__(self):
            self.chromium = _FakeChromium()

    @asynccontextmanager
    async def _fake_async_playwright():
        yield _FakePW()

    return _fake_async_playwright


def test_base_scraper_log_always_prefixes_shop_name_without_duplication():
    logs: list[str] = []
    scraper = _DummyScraper(shop_name="Triguetech", base_url="https://www.triguetech.es")
    scraper.log_callback = logs.append

    scraper._log("📄 Página 1: 40 productos")
    scraper._log("🧭 [Triguetech] Accediendo a página 2...")
    scraper._log("Triguetech: inicio manual")

    assert logs[0] == "[Triguetech] 📄 Página 1: 40 productos"
    assert logs[1] == "🧭 [Triguetech] Accediendo a página 2..."
    assert logs[2] == "Triguetech: inicio manual"


@pytest.mark.asyncio
async def test_base_scraper_safe_navigate_detects_pageindex_s_path_and_page_segment():
    logs: list[str] = []
    scraper = _DummyScraper(shop_name="NavCheck", base_url="https://example.com")
    scraper.log_callback = logs.append

    fake_page = MagicMock()
    fake_page.goto = AsyncMock(return_value=None)

    await scraper._safe_navigate(fake_page, "https://www.bigbadtoystore.com/Search?SearchText=motu&PageIndex=2")
    await scraper._safe_navigate(fake_page, "https://www.toymi.eu/Masters-of-the-Universe_s3?af=60")
    await scraper._safe_navigate(fake_page, "https://www.triguetech.es/categoria-producto/motu/page/4/")
    await scraper._safe_navigate(fake_page, "https://bixoto.com/es/u/games?search=motu&page=5")

    assert any("página 2" in m.lower() for m in logs), logs
    assert any("página 3" in m.lower() for m in logs), logs
    assert any("página 4" in m.lower() for m in logs), logs
    assert any("página 5" in m.lower() for m in logs), logs


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "module_path,class_name,shop_name,html_pages",
    [
        (
            "src.infrastructure.scrapers.electropolis_scraper",
            "ElectropolisScraper",
            "Electropolis",
            [
                '<div class="product-item-info"><a class="product-item-link" href="https://www.electropolis.es/he-man">He-Man Origins</a><span data-price-type="finalPrice" data-price-amount="19.95"></span></div>',
            ],
        ),
        (
            "src.infrastructure.scrapers.frikiverso_scraper",
            "FrikiversoScraper",
            "Frikiverso",
            [
                '<article class="js-product-miniature"><div class="product-title"><a href="https://frikiverso.es/skeletor">Skeletor Origins</a></div><div class="product-price-and-shipping"><span class="price">21,50 €</span></div></article>',
            ],
        ),
        (
            "src.infrastructure.scrapers.pixelatoy_scraper",
            "PixelatoyScraper",
            "Pixelatoy",
            [
                '<article class="product-miniature"><h3 class="product-title"><a href="https://www.pixelatoy.com/es/man-at-arms">Man-At-Arms Origins</a></h3><span class="product-price" content="18.90">18,90 €</span></article>',
            ],
        ),
        (
            "src.infrastructure.scrapers.detoyboys_scraper",
            "DeToyboysNLScraper",
            "DeToyboys",
            [
                '<li class="ajax_block_product"><a class="product-name" href="/en/beast-man">Beast Man Origins</a><span class="price product-price">22,00 €</span></li>',
            ],
        ),
        (
            "src.infrastructure.scrapers.toymi_scraper",
            "ToymiEUScraper",
            "ToymiEU",
            [
                '<div><a href="/Mattel-He-Man-Masters-of-the-Universe-Origins">Mattel He-Man Masters of the Universe Origins</a><span class="price">19,99 €</span></div>',
                '<div></div>',
            ],
        ),
        (
            "src.infrastructure.scrapers.time4actiontoys_scraper",
            "Time4ActionToysDEScraper",
            "Time4ActionToysDE",
            [
                '<div class="product-box"><a href="/motu-teela"><span class="product-name">Teela MOTU Origins</span></a><span class="price">17,95 €</span></div>',
                '<html><body></body></html>',
            ],
        ),
        (
            "src.infrastructure.scrapers.bbts_scraper",
            "BigBadToyStoreScraper",
            "BigBadToyStore",
            [
                '<div class="search-item"><a href="/Product/VariationDetails/12345"></a><h2 class="product-name">Masters of the Universe Origins Trap Jaw</h2><span class="product-price">$19.99</span></div>',
            ],
        ),
    ],
)
async def test_previously_silent_playwright_scrapers_log_page_and_total_to_ui(
    module_path, class_name, shop_name, html_pages, monkeypatch
):
    import importlib
    import playwright.async_api as pw_mod

    mod = importlib.import_module(module_path)
    scraper = getattr(mod, class_name)()
    logs: list[str] = []
    scraper.log_callback = logs.append
    scraper.max_pages = 2

    monkeypatch.setattr(pw_mod, "async_playwright", _make_fake_playwright(html_pages))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock(return_value=None))
    monkeypatch.setattr(scraper, "_random_sleep", AsyncMock(return_value=None))

    offers = await scraper.search("auto")
    assert len(offers) >= 1

    assert any(shop_name in m and "página 1" in m.lower() and re.search(r":\s*\d+", m) for m in logs), (
        f"{shop_name} must emit per-page count to log_callback; got: {logs}"
    )
    assert any(shop_name in m and "total" in m.lower() and str(len(offers)) in m for m in logs), (
        f"{shop_name} must emit final total to log_callback; got: {logs}"
    )


@pytest.mark.asyncio
async def test_http_and_hybrid_scrapers_log_page_and_total_with_shop_prefix(monkeypatch):
    from src.infrastructure.scrapers.fantasia_scraper import FantasiaScraper
    from src.infrastructure.scrapers.frikimaz_scraper import FrikimazScraper
    from src.infrastructure.scrapers.triguetech_scraper import TriguetechScraper
    from src.infrastructure.scrapers.lamansiondelterror_scraper import LaMansionDelTerrorScraper
    from src.infrastructure.scrapers.bixoto_scraper import BixotoScraper
    from src.infrastructure.scrapers.ebay_scraper import EbayScraper
    from src.infrastructure.scrapers.vinted_scraper import VintedScraper
    from src.infrastructure.scrapers.wallapop_manual_scraper import WallapopManualScraper
    from src.infrastructure.scrapers.amazon_scraper import AmazonScraper
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper

    monkeypatch.setattr(asyncio, "sleep", AsyncMock(return_value=None))

    # 1. Fantasia
    fan = FantasiaScraper()
    fan_logs: list[str] = []
    fan.log_callback = fan_logs.append
    fan._curl_get = AsyncMock(
        side_effect=[
            '<article class="product-miniature"><h2 class="product-title"><a href="https://fantasiapersonajes.es/he-man-origins">He-Man Origins</a></h2><span class="price">18,95 €</span></article>',
            None,
        ]
    )
    fan_res = await fan.search("auto")
    assert len(fan_res) == 1
    assert any("Fantasia Personajes" in m and "Página 1" in m and "1" in m for m in fan_logs), fan_logs
    assert any("Fantasia Personajes" in m and "Total" in m and "1" in m for m in fan_logs), fan_logs

    # 2. Frikimaz
    fmz = FrikimazScraper()
    fmz_logs: list[str] = []
    fmz.log_callback = fmz_logs.append
    fmz._curl_get = AsyncMock(
        return_value='<article class="product-miniature"><h3 class="product-title"><a href="https://frikimaz.es/skeletor">Skeletor Origins</a></h3><span class="price">19,90 €</span></article>'
    )
    fmz_res = await fmz.search("auto")
    assert len(fmz_res) == 1
    assert any("[Frikimaz]" in m and "Página 1" in m for m in fmz_logs), fmz_logs
    assert any("[Frikimaz]" in m and "Total" in m for m in fmz_logs), fmz_logs

    # 3. Triguetech
    trg = TriguetechScraper()
    trg_logs: list[str] = []
    trg.log_callback = trg_logs.append
    trg._curl_get = AsyncMock(
        return_value='<li class="product type-product"><h2 class="woocommerce-loop-product__title"><a href="https://www.triguetech.es/p/teela">Teela Origins</a></h2><span class="price"><span class="woocommerce-Price-amount amount"><bdi>17,50 €</bdi></span></span></li>'
    )
    trg_res = await trg.search("auto")
    assert len(trg_res) == 1
    assert any("[Triguetech]" in m and "Página 1" in m for m in trg_logs), trg_logs
    assert any("[Triguetech]" in m and "Total" in m for m in trg_logs), trg_logs

    # 4. LaMansionDelTerror
    lmt = LaMansionDelTerrorScraper()
    lmt_logs: list[str] = []
    lmt.log_callback = lmt_logs.append
    lmt._curl_get = AsyncMock(
        return_value='<div class="product"><h3><a href="https://lamansiondelterror.es/p/orko">Orko Origins</a></h3><span class="sale">16,95 €</span></div>'
    )
    lmt_res = await lmt.search("auto")
    assert len(lmt_res) == 1
    assert any("[LaMansionDelTerror]" in m and "Página 1" in m for m in lmt_logs), lmt_logs
    assert any("[LaMansionDelTerror]" in m and "Total" in m for m in lmt_logs), lmt_logs

    # 5. Bixoto (query context in per-page log)
    bix = BixotoScraper()
    bix_logs: list[str] = []
    bix.log_callback = bix_logs.append
    bix._curl_get = AsyncMock(
        return_value='<div class="product-card"><a href="/es/p/motu-he-man"><span class="product-card__name">MOTU Origins He-Man</span></a><div class="price">18,00 €</div></div>'
    )
    bix_res = await bix.search("auto")
    assert len(bix_res) == 1
    assert any("Consulta 1/3" in m and "Página 1" in m for m in bix_logs), bix_logs

    # 6. SmythsToys (Nivel 1 + total)
    smy = SmythsToysScraper()
    smy_logs: list[str] = []
    smy.log_callback = smy_logs.append
    nuxt_payload = [
        ["ShallowReactive", 1],
        {"products": 2},
        [3],
        {"code": 4, "name": 5, "url": 6, "metadata": 7},
        "111",
        "Masters of the Universe Origins He-Man",
        "/de/de-de/he-man/p/111",
        {"priceDetails": 8},
        {"value": 19.99},
    ]
    smy._fast_infiltration = AsyncMock(
        side_effect=lambda q: smy._extract_offers_from_html(
            f'<script id="__NUXT_DATA__" type="application/json">{json.dumps(nuxt_payload)}</script>',
            set(),
        )
    )
    smy_res = await smy.search("auto")
    assert len(smy_res) == 1
    assert any("SmythsToys" in m and "Página 1" in m for m in smy_logs), smy_logs
    assert any("SmythsToys" in m and "Total" in m for m in smy_logs), smy_logs

    # 7. Amazon.es (Nivel 1 + total)
    amz = AmazonScraper()
    amz_logs: list[str] = []
    amz.log_callback = amz_logs.append
    amz._curl_get = AsyncMock(
        return_value='<div data-asin="B08TEST123"><h2><span>He-Man Origins</span></h2><span class="a-price"><span class="a-offscreen">19,99 €</span></span><a class="a-link-normal" href="/dp/B08TEST123">link</a></div>'
    )
    amz_res = await amz.search("auto")
    assert len(amz_res) == 1
    assert any("Amazon.es" in m and "Página 1" in m for m in amz_logs), amz_logs
    assert any("Amazon.es" in m and "Total" in m for m in amz_logs), amz_logs

    # 8. Ebay.es (curl + total)
    eby = EbayScraper()
    eby_logs: list[str] = []
    eby.log_callback = eby_logs.append
    fake_sess = MagicMock()
    fake_sess.get = AsyncMock(
        return_value=SimpleNamespace(
            status_code=200,
            text='<ul><li class="s-card"><div class="s-card__title">Masters of the Universe Origins Skeletor</div><span class="s-card__price">25,00 EUR</span><a class="s-card__link" href="https://www.ebay.es/itm/123456789012">item</a></li></ul>',
        )
    )
    fake_sess.close = AsyncMock(return_value=None)
    eby._session = fake_sess
    eby._session_headers = eby._get_random_header()
    eby_res = await eby.search("he-man origins")
    assert len(eby_res) == 1
    assert any("Ebay.es" in m and "Total" in m for m in eby_logs), eby_logs

    # 9. Vinted (per-page valid count + total)
    vin = VintedScraper()
    vin_logs: list[str] = []
    vin.log_callback = vin_logs.append
    vin._init_session = AsyncMock(return_value=None)
    v_sess = MagicMock()
    v_sess.get = AsyncMock(
        side_effect=[
            SimpleNamespace(
                status_code=200,
                text='<a data-testid="product-item-id-999--overlay-link" href="/items/999-he-man-origins" title="He-Man Origins, Marca: Mattel"></a><span data-testid="product-item-id-999--price-text">15,00 €</span>',
            ),
            SimpleNamespace(status_code=200, text="<html></html>"),
        ]
    )
    v_sess.close = AsyncMock(return_value=None)
    vin._session = v_sess
    vin_res = await vin.search("motu origins")
    assert len(vin_res) == 1
    assert any("Vinted" in m and "Página 1" in m and "ofertas válidas" in m.lower() for m in vin_logs), vin_logs
    assert any("Vinted" in m and "Total" in m for m in vin_logs), vin_logs

    # 10. WallapopManual (per-page log + total)
    wal = WallapopManualScraper()
    wal_logs: list[str] = []
    wal.log_callback = wal_logs.append
    wal._search_single = AsyncMock(
        return_value=SimpleNamespace(
            offers=[
                ScrapedOffer(
                    product_name="He-Man Origins",
                    price=15.0,
                    url="https://es.wallapop.com/item/he-man-1",
                    shop_name="Wallapop",
                )
            ],
            blocked=False,
            next_page=None,
        )
    )
    wal_res = await wal.search("he-man origins")
    assert len(wal_res) == 1
    assert any("Wallapop" in m and "Página 1" in m for m in wal_logs), wal_logs
    assert any("Wallapop" in m and "Total" in m or "reliquias únicas" in m for m in wal_logs), wal_logs


@pytest.mark.asyncio
async def test_smythstoys_scraperapi_failures_preserve_blocked_true(monkeypatch):
    from src.infrastructure.scrapers.smythstoys_scraper import SmythsToysScraper

    # Case 1: Missing SCRAPERAPI_KEY
    monkeypatch.delenv("SCRAPERAPI_KEY", raising=False)
    s1 = SmythsToysScraper()
    assert await s1._search_option_2("auto") == []
    assert s1.errors >= 1
    assert s1.blocked is True

    # Case 2: HTTP 500 from ScraperAPI
    monkeypatch.setenv("SCRAPERAPI_KEY", "dummy-key")
    s2 = SmythsToysScraper()
    fake_session = MagicMock()
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=False)
    fake_session.get = AsyncMock(return_value=SimpleNamespace(status_code=500, text="Server Error"))

    with patch("src.infrastructure.scrapers.smythstoys_scraper.AsyncSession", return_value=fake_session):
        res = await s2._search_option_2("auto")
    assert res == []
    assert s2.errors >= 1
    assert s2.blocked is True

    # Case 3: Network/timeout exception
    s3 = SmythsToysScraper()
    fake_err_session = MagicMock()
    fake_err_session.__aenter__ = AsyncMock(return_value=fake_err_session)
    fake_err_session.__aexit__ = AsyncMock(return_value=False)
    fake_err_session.get = AsyncMock(side_effect=RuntimeError("timeout"))

    with patch("src.infrastructure.scrapers.smythstoys_scraper.AsyncSession", return_value=fake_err_session):
        res3 = await s3._search_option_2("auto")
    assert res3 == []
    assert s3.errors >= 1
    assert s3.blocked is True


def test_run_scraper_task_all_excludes_zero_offer_shops_from_deactivation(client):
    from datetime import timezone
    from src.interfaces.api.routers.scrapers import run_scraper_task

    empty_shop = MagicMock()
    empty_shop.shop_name = "SmythsToys"
    empty_shop.spider_name = "SmythsToys"
    empty_shop.blocked = False
    empty_shop.errors = 0
    empty_shop.search = AsyncMock(return_value=[])

    active_shop = MagicMock()
    active_shop.shop_name = "Triguetech"
    active_shop.spider_name = "Triguetech"
    active_shop.blocked = False
    active_shop.errors = 0
    active_shop.search = AsyncMock(
        return_value=[
            ScrapedOffer(
                product_name="He-Man Origins",
                price=19.99,
                url="https://triguetech.es/he-man",
                shop_name="Triguetech",
            )
        ]
    )

    captured_shop_names: list[list[str]] = []

    def fake_update_db(self, offers, shop_names=None, allow_deactivation=True):
        captured_shop_names.append(list(shop_names or []))
        return 0

    with patch("src.infrastructure.scrapers.smythstoys_scraper.SmythsToysScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.triguetech_scraper.TriguetechScraper", return_value=active_shop), \
         patch("src.infrastructure.scrapers.fantasia_scraper.FantasiaScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.frikiverso_scraper.FrikiversoScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.frikimaz_scraper.FrikimazScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.electropolis_scraper.ElectropolisScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.pixelatoy_scraper.PixelatoyScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.amazon_scraper.AmazonScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.detoyboys_scraper.DeToyboysNLScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.ebay_scraper.EbayScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.vinted_scraper.VintedScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.wallapop_manual_scraper.WallapopManualScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.toymi_scraper.ToymiEUScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.bixoto_scraper.BixotoScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.time4actiontoys_scraper.Time4ActionToysDEScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.bbts_scraper.BigBadToyStoreScraper", return_value=empty_shop), \
         patch("src.infrastructure.scrapers.lamansiondelterror_scraper.LaMansionDelTerrorScraper", return_value=empty_shop), \
         patch("src.interfaces.api.routers.scrapers._get_madrid_tz", return_value=timezone.utc), \
         patch("src.infrastructure.scrapers.pipeline.ScrapingPipeline.update_database", new=fake_update_db):
        run_scraper_task("all", trigger_type="manual")

    assert len(captured_shop_names) == 1
    assert "Triguetech" in captured_shop_names[0]
    assert "SmythsToys" not in captured_shop_names[0]


def test_daily_scan_uses_cloud_session_and_case_insensitive_smythstoys_fallback():
    import src.application.jobs.daily_scan as daily_scan
    from src.infrastructure.database_cloud import SessionCloud

    # In tests, SessionCloud & daily_scan.SessionLocal are patched identically by conftest; verify module binding or alias
    source = inspect.getsource(daily_scan)
    assert "SessionCloud as SessionLocal" in source
    assert "scraper.spider_name.lower() == \"smythstoys\"" in source
    assert daily_scan.SessionLocal is SessionCloud or "SessionLocal" in str(daily_scan.SessionLocal)


@pytest.mark.asyncio
async def test_pipeline_logs_breakdown_and_errors_to_ui():
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline

    ok_spider = _DummyScraper(shop_name="Triguetech")
    ok_spider.search = AsyncMock(
        return_value=[
            ScrapedOffer(
                product_name="He-Man Origins",
                price=19.99,
                url="https://triguetech.es/1",
                shop_name="Triguetech",
            )
        ]
    )

    err_spider = _DummyScraper(shop_name="SmythsToys")
    err_spider.search = AsyncMock(side_effect=asyncio.TimeoutError())

    logs: list[str] = []
    pipeline = ScrapingPipeline([ok_spider, err_spider])
    pipeline.log_callback = logs.append

    with patch("src.infrastructure.scrapers.adapter.adapter.transform", side_effect=lambda x: x):
        results = await pipeline.run_product_search("auto")

    assert len(results) == 1
    assert pipeline.per_shop_counts == {"Triguetech": 1, "SmythsToys": 0}
    assert "SmythsToys" in pipeline.failed_spiders
    assert any("[SmythsToys] Timeout" in m for m in logs), logs
    assert any("[Desglose por Tienda]" in m and "Triguetech: 1" in m and "SmythsToys: 0" in m for m in logs), logs
