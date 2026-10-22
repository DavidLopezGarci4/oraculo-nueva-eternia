"""
Tests de cohesión y rendimiento para WU-6:
- PERF-08: CurrencyService negative-cache backoff cuando falla XE.com (1 intento HTTP en lugar de N).
- PERF-09: LoreHarvesterService.seed_initial_catalog actualiza sólo productos con character_slug nulo/vacío.
- PERF-11: ScrapingPipeline.update_database y ProductRepository.add_offer sin tormenta N+1 ni flush por oferta existente.
- PERF-12: ScrapingPipeline.run_product_search usa doble semáforo (browser_sem=1 vs http_sem=4).
- PERF-13: Notificaciones asíncronas de Telegram en update_database se ejecutan sin RuntimeError cuando el event loop sigue abierto.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import requests
from sqlalchemy import event

from src.application.services.currency_service import CurrencyService
from src.application.services.lore_harvester_service import LoreHarvesterService
from src.domain.models import (
    CollectionItemModel,
    OfferModel,
    PendingMatchModel,
    PriceAlertModel,
    PriceHistoryModel,
    ProductModel,
    UserModel,
)
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from tests.conftest import _TestSession


def test_wu6_currency_service_negative_cache_backoff():
    """
    Si XE.com cae o da timeout, CurrencyService debe fijar un backoff en _cache['expiry']
    para no reintentar requests.get(timeout=10) en cada oferta USD del lote.
    """
    CurrencyService._cache = {"rate": 0.92, "expiry": datetime.min}

    with patch("src.application.services.currency_service.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("XE timeout")

        rates = [CurrencyService.get_usd_to_eur_rate() for _ in range(10)]

        assert all(r == 0.92 for r in rates)
        assert mock_get.call_count == 1, (
            f"Expected 1 HTTP call due to negative-cache backoff, got {mock_get.call_count}"
        )


def test_wu6_lore_seed_initial_catalog_skips_already_linked_products(client):
    """
    LoreHarvesterService.seed_initial_catalog sólo debe vincular productos cuyo
    character_slug sea None o vacío, evitando reescribir los 507 productos en cada arranque.
    """
    with _TestSession() as db:
        # Baseline any products left by previous tests in the shared test DB
        LoreHarvesterService.seed_initial_catalog(db)

        p1 = ProductModel(
            name="He-Man",
            category="Action Figures",
            sub_category="Origins",
            figure_id="WU6-LORE-1",
            is_vintage=False,
            character_slug="he_man",
        )
        p2 = ProductModel(
            name="Skeletor",
            category="Action Figures",
            sub_category="Origins",
            figure_id="WU6-LORE-2",
            is_vintage=False,
            character_slug=None,
        )
        db.add_all([p1, p2])
        db.commit()

        res1 = LoreHarvesterService.seed_initial_catalog(db)
        assert res1["linked_products"] == 1, f"Expected only 1 unlinked product updated, got {res1}"

        res2 = LoreHarvesterService.seed_initial_catalog(db)
        assert res2["linked_products"] == 0, f"Expected 0 products updated on second run, got {res2}"
        assert res2["seeded_characters"] == 0


def test_wu6_pipeline_dual_semaphore_browser_vs_http():
    """
    ScrapingPipeline.run_product_search debe serializar los scrapers de navegador
    (browser_sem=1) mientras permite concurrencia en scrapers HTTP (http_sem=4).
    """
    active_browser = 0
    max_active_browser = 0
    active_http = 0
    max_active_http = 0

    class DummyBrowserScraper(BaseScraper):
        uses_browser = True

        async def search(self, query: str):
            nonlocal active_browser, max_active_browser
            active_browser += 1
            max_active_browser = max(max_active_browser, active_browser)
            await asyncio.sleep(0.06)
            active_browser -= 1
            return [
                ScrapedOffer(
                    product_name=f"MOTU Origins He-Man {self.shop_name}",
                    price=19.99,
                    url=f"https://example.com/{self.shop_name}/1",
                    shop_name=self.shop_name,
                )
            ]

    class DummyHttpScraper(BaseScraper):
        uses_browser = False

        async def search(self, query: str):
            nonlocal active_http, max_active_http
            active_http += 1
            max_active_http = max(max_active_http, active_http)
            await asyncio.sleep(0.06)
            active_http -= 1
            return [
                ScrapedOffer(
                    product_name=f"MOTU Origins Skeletor {self.shop_name}",
                    price=21.99,
                    url=f"https://example.com/{self.shop_name}/2",
                    shop_name=self.shop_name,
                )
            ]

    scrapers = [
        DummyBrowserScraper("BrowserShop1"),
        DummyBrowserScraper("BrowserShop2"),
        DummyHttpScraper("HttpShop1"),
        DummyHttpScraper("HttpShop2"),
        DummyHttpScraper("HttpShop3"),
    ]
    pipeline = ScrapingPipeline(scrapers)

    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(pipeline.run_product_search("he-man"))
    finally:
        loop.close()

    assert len(results) == 5
    assert max_active_browser == 1, f"Browser scrapers must not exceed 1 concurrent instance, got {max_active_browser}"
    assert max_active_http >= 2, f"HTTP scrapers should run concurrently (expected >=2), got {max_active_http}"


def test_wu6_pipeline_update_database_no_n_plus_1_and_telegram_tasks(client):
    """
    ScrapingPipeline.update_database debe procesar lotes de ofertas existentes y nuevas
    en Purgatorio con un número constante de SELECTs (sin N+1 por oferta ni por alerta multiusuario)
    y ejecutar tareas de Telegram en el event loop activo sin RuntimeError.
    """
    with _TestSession() as db:
        engine = db.get_bind()

        user = db.query(UserModel).filter(UserModel.id == 2).first()
        if not user:
            user = UserModel(
                id=2,
                username="arquitecto",
                email="admin@eternia.com",
                hashed_password="x",
                role="admin",
                is_active=True,
                telegram_chat_id="12345678",
            )
            db.add(user)
        else:
            user.telegram_chat_id = "12345678"
            user.is_active = True
        db.commit()

        products = []
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        for i in range(10):
            p = ProductModel(
                name=f"Origins Guard {i}",
                category="Action Figures",
                sub_category="Origins",
                figure_id=f"WU6-P-{i}",
                is_vintage=False,
                retail_price=20.0,
                avg_market_price=25.0,
            )
            db.add(p)
            db.flush()
            products.append(p)

            off = OfferModel(
                product_id=p.id,
                shop_name="Fantasia Personajes",
                price=22.0,
                min_price=22.0,
                max_price=25.0,
                url=f"https://fantasia.test/item-{i}",
                is_available=True,
                source_type="Retail",
                last_seen=now_naive,
            )
            db.add(off)
            db.flush()
            db.add(PriceHistoryModel(offer_id=off.id, price=22.0, recorded_at=now_naive))

        # Wishlist item & PriceAlert for user 2 to trigger multiuser alerts on new Purgatory items
        wish_prod = products[0]
        db.add(CollectionItemModel(owner_id=2, product_id=wish_prod.id, acquired=False))
        db.add(PriceAlertModel(user_id=2, product_id=wish_prod.id, target_price=30.0, is_active=True))
        db.commit()

    incoming_batch = []
    # 10 existing offers (5 unchanged price, 5 changed price)
    for i in range(10):
        incoming_batch.append(
            {
                "product_name": f"MOTU Origins Guard {i}",
                "price": 22.0 if i < 5 else 19.5,
                "currency": "EUR",
                "url": f"https://fantasia.test/item-{i}",
                "shop_name": "Fantasia Personajes",
                "is_available": True,
                "source_type": "Retail",
            }
        )
    # 5 new Purgatory offers matching wishlist words ("Origins Guard")
    for j in range(5):
        incoming_batch.append(
            {
                "product_name": f"MOTU Origins Guard 0 Nuevo {j}",
                "price": 18.0,
                "currency": "EUR",
                "url": f"https://fantasia.test/new-item-{j}",
                "shop_name": "Fantasia Personajes",
                "is_available": True,
                "source_type": "Retail",
            }
        )

    select_queries: list[str] = []

    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        sql = statement.strip().upper()
        if sql.startswith("SELECT"):
            select_queries.append(statement)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    event.listen(engine, "before_cursor_execute", _before_cursor_execute)
    try:
        with patch("src.core.backup_manager.BackupManager.save_raw_snapshot"), patch(
            "src.infrastructure.services.telegram_service.telegram_service.send_wishlist_alert",
            new_callable=AsyncMock,
        ) as mock_wish_alert, patch(
            "src.infrastructure.services.telegram_service.telegram_service.send_price_alert",
            new_callable=AsyncMock,
        ) as mock_price_alert:
            pipeline = ScrapingPipeline([])
            new_count = pipeline.update_database(incoming_batch, shop_names=["Fantasia Personajes"])
            assert new_count == 5
            assert mock_wish_alert.await_count >= 5
            assert mock_price_alert.await_count >= 5
    finally:
        event.remove(engine, "before_cursor_execute", _before_cursor_execute)
        loop.close()

    # Con precarga en bloque (existing_offers + joinedload, last_snapshot en lote, y alert_context precargado),
    # el total de SELECTs para 15 ofertas debe ser <= 16 (antes superaba 45 SELECTs).
    assert len(select_queries) <= 16, (
        f"Expected <= 16 SELECT queries in update_database, got {len(select_queries)}:\n"
        + "\n---\n".join(select_queries)
    )

    with _TestSession() as db:
        assert (
            db.query(PendingMatchModel)
            .filter(PendingMatchModel.url.like("https://fantasia.test/new-item-%"))
            .count()
            == 5
        )
        updated_off = db.query(OfferModel).filter(OfferModel.url == "https://fantasia.test/item-6").first()
        assert updated_off is not None and abs(updated_off.price - 19.5) < 0.01
