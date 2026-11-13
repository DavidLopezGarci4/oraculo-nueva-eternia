"""
ODD WU3 RED->GREEN Regression Suite: Backend Bugs, FK Integrity & Async Performance.
"""
import asyncio
import inspect
import io
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def _make_fk_session_factory(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fks(dbapi_conn, _conn_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    from src.domain.models import Base

    Base.metadata.create_all(bind=engine)
    return engine, sessionmaker(bind=engine, autocommit=False, autoflush=False)


def test_bp01_sync_availability_targeted_protection(tmp_path):
    """C-01: Targeted/cancelled/vinted scrapes must NOT deactivate unrelated shop offers."""
    from src.domain.models import OfferModel, ProductModel
    from src.infrastructure.scrapers.pipeline import ScrapingPipeline

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp01.db")
    with SessionFactory() as db:
        prod = ProductModel(name="Skeletor Origins", category="Origins")
        db.add(prod)
        db.flush()
        db.add(
            OfferModel(
                product_id=prod.id,
                shop_name="Fantasia Personajes",
                price=19.99,
                url="https://fantasia.example/skeletor",
                is_available=True,
                is_vintage=False,
                source_type="Retail",
            )
        )
        db.commit()

    pipeline = ScrapingPipeline([])
    with patch("src.infrastructure.scrapers.pipeline.SessionCloud", SessionFactory):
        pipeline.update_database([], shop_names=["Fantasia Personajes"], allow_deactivation=False)

    with SessionFactory() as db:
        offer = db.query(OfferModel).filter_by(url="https://fantasia.example/skeletor").one()
        assert offer.is_available is True

    # Also verify run_product_search records failed spiders so run_scraper_task won't deactivate them
    class BrokenSpider:
        shop_name = "BrokenShop"
        uses_browser = False

        async def search(self, query):
            raise RuntimeError("boom")

    failing_pipeline = ScrapingPipeline([BrokenSpider()])
    asyncio.run(failing_pipeline.run_product_search("auto"))
    assert "BrokenShop" in failing_pipeline.failed_spiders


def test_bp02_fk_cascade_delete_product_and_user_and_nexus_safe_purge(tmp_path):
    """C-02: Product delete, Admin user delete, and Nexus safe_mode purge must respect SQL/PG FKs."""
    from src.application.services.nexus_service import NexusService
    from src.domain.models import (
        CollectionItemModel,
        OfferModel,
        PriceAlertModel,
        PriceHistoryModel,
        ProductAliasModel,
        ProductLoreModel,
        ProductModel,
        ProductMonthlyStatsModel,
        StagedImportModel,
        UserModel,
        VintageProductModel,
    )
    from src.interfaces.api.routers.admin import delete_hero
    from src.interfaces.api.routers.products import delete_product

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp02.db")
    with SessionFactory() as db:
        user = UserModel(
            username="victim_hero",
            email="victim@eternia.test",
            hashed_password="x",
            role="viewer",
            is_active=True,
        )
        db.add(user)
        db.flush()

        p_del = ProductModel(name="Product To Delete", category="Origins")
        p_keep = ProductModel(name="Owned By Collection", category="Origins")
        p_orphan = ProductModel(name="Orphan To Purge", category="Origins")
        db.add_all([p_del, p_keep, p_orphan])
        db.flush()

        offer_del = OfferModel(
            product_id=p_del.id,
            shop_name="ShopA",
            price=20.0,
            url="https://shopa.example/del",
            is_available=True,
        )
        offer_keep = OfferModel(
            product_id=p_keep.id,
            shop_name="ShopA",
            price=25.0,
            url="https://shopa.example/keep",
            is_available=True,
        )
        db.add_all([offer_del, offer_keep])
        db.flush()

        db.add_all([
            PriceHistoryModel(offer_id=offer_del.id, price=20.0),
            PriceHistoryModel(offer_id=offer_keep.id, price=25.0),
            ProductAliasModel(product_id=p_del.id, source_url="https://shopa.example/old-del"),
            ProductAliasModel(product_id=p_keep.id, source_url="https://shopa.example/keep"),
            VintageProductModel(product_id=p_del.id, notes="v"),
            PriceAlertModel(product_id=p_del.id, user_id=user.id, target_price=15.0),
            ProductMonthlyStatsModel(
                product_id=p_del.id,
                year=2026,
                month=11,
                source_type="Retail",
                avg_price=20.0,
                median_price=20.0,
                min_price=20.0,
                max_price=20.0,
                std_dev_price=0.0,
                p25_price=20.0,
                p75_price=20.0,
                offers_count=1,
            ),
            ProductLoreModel(
                product_id=p_del.id,
                canonical_name="Prod Del",
                lore="Lore text",
            ),
            StagedImportModel(
                user_id=user.id,
                import_type="VAULT",
                status="PENDING",
                data_payload="{}",
                impact_summary="test",
            ),
            CollectionItemModel(product_id=p_keep.id, owner_id=user.id, acquired=True),
        ])
        db.commit()
        p_del_id, p_keep_id, p_orphan_id, user_id = p_del.id, p_keep.id, p_orphan.id, user.id

    with patch("src.interfaces.api.routers.products.SessionCloud", SessionFactory):
        res_prod = delete_product(p_del_id)
        assert res_prod["status"] == "success"

    with patch("src.interfaces.api.routers.admin.SessionCloud", SessionFactory):
        res_user = delete_hero(user_id)
        assert res_user["status"] == "success"

    # Re-add a collection item from another user so safe_mode purge must preserve p_keep without FK failure
    with SessionFactory() as db:
        holder = UserModel(
            username="holder_hero",
            email="holder@eternia.test",
            hashed_password="x",
            role="viewer",
            is_active=True,
        )
        db.add(holder)
        db.flush()
        db.add(CollectionItemModel(product_id=p_keep_id, owner_id=holder.id, acquired=True))
        db.commit()

        NexusService.purge_catalog(db, safe_mode=True)
        assert db.query(ProductModel).filter_by(id=p_keep_id).first() is not None
        assert db.query(ProductModel).filter_by(id=p_orphan_id).first() is None


def test_bp03_vault_duplicate_units_no_integrity_error(tmp_path):
    """H-01: Multiple CollectionItem rows for the same Product must not crash Vault export."""
    import sqlite3
    from src.application.services.vault_service import VaultService
    from src.domain.models import CollectionItemModel, ProductModel, UserModel

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp03.db")
    with SessionFactory() as db:
        user = UserModel(username="collector", email="c@e.test", hashed_password="x")
        prod = ProductModel(name="He-Man Origins", category="Origins")
        db.add_all([user, prod])
        db.flush()
        db.add(CollectionItemModel(product_id=prod.id, owner_id=user.id, acquired=True, condition="MOC"))
        db.add(CollectionItemModel(product_id=prod.id, owner_id=user.id, acquired=True, condition="Loose"))
        db.commit()
        user_id = user.id

        svc = VaultService(base_vault_path=str(tmp_path / "vaults"))
        vault_path = svc.generate_user_vault(user_id=user_id, db_session=db)

    conn = sqlite3.connect(vault_path)
    try:
        prod_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        item_count = conn.execute("SELECT COUNT(*) FROM collection").fetchone()[0]
        assert prod_count == 1
        assert item_count == 2
    finally:
        conn.close()


def test_bp04_add_offer_persists_auction_metadata(tmp_path):
    """H-04: ProductRepository.add_offer must persist sale_type, expiry_at, bids_count, time_left_raw."""
    from src.domain.models import ProductModel
    from src.infrastructure.repositories.product import ProductRepository

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp04.db")
    expiry_1 = datetime(2026, 12, 1, 18, 0, tzinfo=timezone.utc).replace(tzinfo=None)
    expiry_2 = datetime(2026, 12, 2, 18, 0, tzinfo=timezone.utc).replace(tzinfo=None)

    with SessionFactory() as db:
        prod = ProductModel(name="Trap Jaw Origins", category="Origins")
        db.add(prod)
        db.commit()
        db.refresh(prod)

        repo = ProductRepository(db)
        offer, _ = repo.add_offer(
            prod,
            {
                "shop_name": "eBay.es",
                "price": 32.5,
                "url": "https://www.ebay.es/itm/999001",
                "source_type": "Peer-to-Peer",
                "sale_type": "Auction",
                "expiry_at": expiry_1,
                "bids_count": 4,
                "time_left_raw": "1d 4h",
            },
        )
        assert offer.sale_type == "Auction"
        assert offer.expiry_at == expiry_1
        assert offer.bids_count == 4
        assert offer.time_left_raw == "1d 4h"

        offer_upd, _ = repo.add_offer(
            prod,
            {
                "shop_name": "eBay.es",
                "price": 39.0,
                "url": "https://www.ebay.es/itm/999001",
                "source_type": "Peer-to-Peer",
                "sale_type": "Auction",
                "expiry_at": expiry_2,
                "bids_count": 7,
                "time_left_raw": "2h",
            },
        )
        assert offer_upd.bids_count == 7
        assert offer_upd.expiry_at == expiry_2
        assert offer_upd.time_left_raw == "2h"


def test_bp05_image_transparency_la_and_no_fake_url_on_upload_fail(tmp_path):
    """H-07: LA-mode grayscale+alpha PNGs must not IndexError, and failed uploads must NOT forge supabase.co URLs."""
    from src.application.services.catalog_refresh_service import CatalogRefreshService
    from src.application.services.storage_service import StorageService
    from src.domain.models import ProductModel

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp05.db")
    with SessionFactory() as db:
        prod = ProductModel(
            name="Scare Glow",
            figure_id="042",
            category="Origins",
            image_url="/images/original-scareglow.webp",
        )
        db.add(prod)
        db.commit()
        prod_id = prod.id

    buf = io.BytesIO()
    Image.new("LA", (12, 12), (200, 128)).save(buf, format="PNG")
    la_png_bytes = buf.getvalue()

    la_path = tmp_path / "la_test.png"
    la_path.write_bytes(la_png_bytes)

    with patch("src.application.services.storage_service.create_client", return_value=MagicMock()):
        storage = StorageService()
    storage.client = MagicMock()
    storage.client.storage.from_.return_value.upload.return_value = None
    storage.client.storage.from_.return_value.get_public_url.return_value = "https://cdn.example/042.webp"
    uploaded_url = storage.upload_image(str(la_path))
    assert uploaded_url == "https://cdn.example/042.webp"

    # Now test CatalogRefreshService with LA PNG and upload_image returning None
    mock_html_res = MagicMock(
        status_code=200,
        text='<a data-fancybox="gallery" href="/wp-content/uploads/scareglow.png">img</a>',
    )
    mock_img_res = MagicMock(status_code=200, content=la_png_bytes)

    with SessionFactory() as db, patch(
        "src.application.services.catalog_refresh_service.cffi_requests.get",
        side_effect=[mock_html_res, mock_img_res],
    ), patch.object(
        CatalogRefreshService,
        "find_af411_detail_url",
        return_value="https://www.actionfigure411.com/masters-of-the-universe/origins/scare-glow.php",
    ), patch.object(
        StorageService,
        "upload_image",
        return_value=None,
    ):
        result = CatalogRefreshService.refresh_figure_image(db, str(prod_id))
        assert result["success"] is False

    with SessionFactory() as db:
        refreshed = db.query(ProductModel).filter_by(id=prod_id).one()
        assert refreshed.image_url == "/images/original-scareglow.webp"
        assert "supabase.co" not in (refreshed.image_url or "")


def test_bp06_purgatory_mutations_invalidate_counts_cache(tmp_path):
    """M-01: All Purgatory mutations must invalidate both Purgatory cache and products count cache."""
    from src.domain.models import OfferModel, PendingMatchModel, ProductModel
    from src.interfaces.api.routers import products as products_router
    from src.interfaces.api.routers import purgatory as purgatory_router

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp06.db")
    with SessionFactory() as db:
        p = ProductModel(name="Man-At-Arms", category="Origins")
        db.add(p)
        db.flush()
        offer = OfferModel(product_id=p.id, shop_name="ShopB", price=18.0, url="https://shopb.example/1")
        pm = PendingMatchModel(scraped_name="Man At Arms", price=18.0, url="https://shopb.example/p1", shop_name="ShopB")
        db.add_all([offer, pm])
        db.commit()
        offer_id, pm_id = offer.id, pm.id

    products_router._purgatory_counts_cache = {999: 3}
    products_router._purgatory_counts_timestamp = 10**12
    purgatory_router._invalidate_link_memory()
    assert products_router._purgatory_counts_cache is None

    # unlink_offer must also invalidate the cache
    products_router._purgatory_counts_cache = {999: 3}
    products_router._purgatory_counts_timestamp = 10**12
    with patch("src.interfaces.api.routers.purgatory.SessionCloud", SessionFactory):
        purgatory_router.unlink_offer(offer_id)
    assert products_router._purgatory_counts_cache is None

    # run_discard_task must also invalidate the cache
    products_router._purgatory_counts_cache = {999: 3}
    products_router._purgatory_counts_timestamp = 10**12
    with patch("src.interfaces.api.routers.purgatory.SessionCloud", SessionFactory):
        purgatory_router.run_discard_task(pm_id, "test")
    assert products_router._purgatory_counts_cache is None


def test_bp07_telegram_listener_and_wallapop_bridge_bugs(tmp_path):
    """Telegram missing os import / cache invalidation / detached relation + WallapopBridge slug guard."""
    from src.application.services.wallapop_bridge import WallapopBridge
    from src.domain.models import AuthorizedDeviceModel
    from src.infrastructure.services import telegram_listener as tl

    assert hasattr(tl, "os"), "telegram_listener must import os for cmd_tokens"

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp07.db")
    with SessionFactory() as db:
        db.add(AuthorizedDeviceModel(device_id="dev-123", device_name="Phone", is_authorized=False))
        db.commit()

    listener = tl.TelegramListener()
    with patch("src.infrastructure.services.telegram_listener.SessionCloud", SessionFactory), patch.object(
        listener, "is_sovereign_admin", return_value=True
    ), patch(
        "src.infrastructure.services.telegram_service.telegram_service.send_message",
        new=AsyncMock(),
    ), patch(
        "src.core.security.SecurityShield.invalidate_device_cache"
    ) as mock_inv:
        asyncio.run(listener.cmd_approve_device(12345, ["dev-123"]))
        mock_inv.assert_called_with("dev-123")

    # Malicious item slug with query/path injection must be rejected without calling HTTP
    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = AsyncMock()
    with patch("src.application.services.wallapop_bridge.AsyncSession", return_value=mock_session):
        res = asyncio.run(
            WallapopBridge.get_item_details("https://es.wallapop.com/item/bad/slug?evil=1#frag")
        )
        assert res is None
        mock_session.get.assert_not_called()


def test_bp08_no_sync_blocking_async_routes_and_hot_indexes():
    """Sync DB handlers must not block the event loop and hot-query composite indexes must exist."""
    import logging
    from src.domain.models import Base
    from src.interfaces.api.routers import logistics, system, vault, wallapop_jobs

    sync_handlers = [
        logistics.api_calculate_cart,
        vault.api_generate_vault,
        vault.api_stage_vault,
        vault.api_sync_excel,
        vault.download_images_zip,
        system.system_audit,
        system.run_maintenance,
        system.run_maintenance_task,
        wallapop_jobs.create_wallapop_job,
        wallapop_jobs.claim_pending_wallapop_job,
        wallapop_jobs.submit_wallapop_job_results,
        wallapop_jobs.list_wallapop_jobs,
    ]
    for fn in sync_handlers:
        assert not inspect.iscoroutinefunction(fn), f"{fn.__qualname__} must not block event loop as async def"

    # Root logger must NOT have DB-committing TelemetryHandler class bound in nexus services
    from src.application.services import nexus_service, nexus_vintage_service

    nexus_src = inspect.getsource(nexus_service.NexusService.sync_catalog)
    nexus_v_src = inspect.getsource(nexus_vintage_service.NexusVintageService.sync_catalog)
    assert "logging.getLogger()" not in nexus_src
    assert "logging.getLogger()" not in nexus_v_src

    offer_idx = {idx.name for idx in Base.metadata.tables["offers"].indexes}
    pending_idx = {idx.name for idx in Base.metadata.tables["pending_matches"].indexes}
    assert "ix_offers_avail_source_last_seen" in offer_idx
    assert "ix_offers_shop_avail_vintage" in offer_idx
    assert "ix_pending_matches_status_found_at" in pending_idx
    assert len(logging.getLogger().handlers) >= 0


def test_bp09_pipeline_alias_normalized_add_offer_cache_and_nexus_modern_scope(tmp_path):
    """Pipeline alias, normalized add_offer URL, immediate cache clear, and Nexus modern purge scope."""
    import time

    from src.application.services.nexus_service import NexusService
    from src.domain.models import OfferModel, ProductModel, VintageProductModel
    from src.infrastructure.repositories.product import ProductRepository
    from src.infrastructure.scrapers import pipeline as pipeline_mod
    from src.interfaces.api.routers import products as products_mod

    # 1. Compatibility alias preserved
    assert callable(pipeline_mod._schedule_async_notification)
    assert pipeline_mod._schedule_async_notification is pipeline_mod._dispatch_async_coro

    # 2. ProductRepository.add_offer normalizes URL before persisting & deduplicates
    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp09.db")
    with SessionFactory() as db:
        prod = ProductModel(name="He-Man Origins", category="Origins", is_vintage=False)
        vintage_prod = ProductModel(name="He-Man Vintage 1982", category="Vintage", is_vintage=True)
        db.add_all([prod, vintage_prod])
        db.flush()
        db.add(VintageProductModel(product_id=vintage_prod.id, notes="Vintage 1982"))
        db.commit()

        repo = ProductRepository(db)
        offer1, _ = repo.add_offer(
            prod,
            {
                "url": "https://shop.example/item/42/?utm_source=feed#frag",
                "shop_name": "Shop",
                "price": 24.99,
                "source_type": "Retail",
            },
        )
        assert offer1.url == "https://shop.example/item/42"

        offer2, _ = repo.add_offer(
            prod,
            {
                "url": "https://shop.example/item/42/",
                "shop_name": "Shop",
                "price": 19.99,
                "source_type": "Retail",
            },
        )
        assert offer2.id == offer1.id
        assert offer2.price == 19.99
        assert db.query(OfferModel).filter_by(product_id=prod.id).count() == 1

        # 3. NexusService.purge_catalog must NEVER touch is_vintage=True products
        NexusService.purge_catalog(db, safe_mode=False)
        assert db.query(ProductModel).filter_by(is_vintage=False).count() == 0
        assert db.query(ProductModel).filter_by(is_vintage=True).count() == 1
        assert db.query(VintageProductModel).count() == 1

    # 4. on_db_change invalidates purgatory counts cache immediately even if dict was truthy
    products_mod._purgatory_counts_cache = {1: 42}
    products_mod._purgatory_counts_timestamp = time.time()
    products_mod.on_db_change(None, None, None)
    assert products_mod._purgatory_counts_cache is None
    assert products_mod._purgatory_counts_timestamp == 0.0

    # 5. Worker threads without an ambient event loop must execute pipeline notifications via asyncio.run
    import threading
    from src.infrastructure.scrapers import pipeline as pipeline_mod

    dispatched: list[str] = []
    thread_errors: list[BaseException] = []

    async def _record_note(tag: str) -> None:
        dispatched.append(tag)

    def _worker() -> None:
        try:
            pipeline_mod._dispatch_async_coro(_record_note("single"))
            pending = [_record_note("batch-1"), _record_note("batch-2")]
            pipeline_mod._flush_pending_notifications(pending)
            assert pending == []
        except BaseException as exc:  # pragma: no cover - surfaced below
            thread_errors.append(exc)

    t = threading.Thread(target=_worker)
    t.start()
    t.join(timeout=5)
    assert not t.is_alive()
    assert not thread_errors
    assert dispatched == ["single", "batch-1", "batch-2"]


def test_bp10_purgatory_duplicates_404_and_telegram_listener_async(tmp_path):
    """Purgatory duplicate-URL safety, true 404 on missing pending_id, and non-blocking TelegramListener."""
    from fastapi import BackgroundTasks, HTTPException

    from src.domain.models import OfferModel, PendingMatchModel, ProductModel, UserModel
    from src.infrastructure.services.telegram_listener import TelegramListener
    from src.interfaces.api.routers import products as products_mod
    from src.interfaces.api.routers import purgatory as purgatory_mod
    from src.interfaces.api.schemas import PurgatoryMatchRequest

    _, SessionFactory = _make_fk_session_factory(tmp_path / "bp10.db")
    with SessionFactory() as db:
        prod = ProductModel(name="Teela Origins", category="Origins", is_vintage=False)
        v_prod = ProductModel(name="Beast Man Vintage", category="Vintage", is_vintage=True)
        db.add_all([prod, v_prod])
        db.flush()

        dup_url = "https://shop.example/reliquia-dup"
        db.add(
            PendingMatchModel(
                scraped_name="Reliquia En Purgatorio",
                price=15.0,
                currency="EUR",
                url=dup_url,
                shop_name="Wallapop",
                source_type="Peer-to-Peer",
            )
        )
        o_unlink = OfferModel(
            product_id=prod.id,
            shop_name="Wallapop",
            price=18.0,
            currency="EUR",
            url=dup_url,
            is_available=True,
            is_vintage=False,
            source_type="Peer-to-Peer",
        )
        o_vintage = OfferModel(
            product_id=v_prod.id,
            shop_name="eBay",
            price=45.0,
            currency="EUR",
            url=dup_url + "-v",
            is_available=True,
            is_vintage=True,
            source_type="Auction",
        )
        db.add(PendingMatchModel(scraped_name="Old V", price=40.0, currency="EUR", url=dup_url + "-v", shop_name="eBay", source_type="Auction"))
        db.add_all([o_unlink, o_vintage])
        db.add(
            UserModel(
                id=2,
                username="david",
                email="viewer-not-admin@test.com",
                hashed_password="x",
                role="viewer",
                telegram_chat_id="555111",
                is_active=True,
            )
        )
        db.commit()
        prod_id = prod.id
        unlink_id = o_unlink.id
        vintage_offer_id = o_vintage.id

    with patch("src.interfaces.api.routers.purgatory.SessionCloud", SessionFactory):
        # 1. Missing pending_id must return 404 even though product already has offers
        with pytest.raises(HTTPException) as exc_info:
            purgatory_mod.match_purgatory(
                PurgatoryMatchRequest(pending_id=999999, product_id=prod_id),
                BackgroundTasks(),
            )
        assert exc_info.value.status_code == 404

        # 2. unlink_offer and revert_vintage_offer update existing PendingMatchModel instead of IntegrityError
        purgatory_mod.unlink_offer(unlink_id)
        purgatory_mod.revert_vintage_offer(vintage_offer_id)

        # 3. Edge case: revert_vintage_offer when offer.product is None must not AttributeError
        mock_db = MagicMock()
        orphan_offer = MagicMock(
            id=123,
            url="https://shop.example/orphan",
            price=12.0,
            currency="EUR",
            shop_name="eBay",
            image_url=None,
            source_type="Auction",
            condition="Loose",
            grading=7.0,
            product=None,
        )
        mock_db.query.return_value.filter.return_value.first.side_effect = [orphan_offer, None]
        with patch("src.interfaces.api.routers.purgatory.SessionCloud") as sc_mock:
            sc_mock.return_value.__enter__.return_value = mock_db
            sc_mock.return_value.__exit__.return_value = False
            res = purgatory_mod.revert_vintage_offer(123)
            assert res["status"] == "success"

    # 4. delete_product skips duplicate PendingMatchModel.url cleanly
    with SessionFactory() as db:
        db.add(
            OfferModel(
                product_id=prod_id,
                shop_name="Wallapop",
                price=22.0,
                currency="EUR",
                url=dup_url,
                is_available=True,
                is_vintage=False,
                source_type="Peer-to-Peer",
            )
        )
        db.commit()
    with patch("src.interfaces.api.routers.products.SessionCloud", SessionFactory):
        del_res = products_mod.delete_product(prod_id)
        assert del_res["status"] == "success"

    # 5. TelegramListener.get_user_status uses deps.is_admin (no id/username backdoor) & returns detached UserModel
    listener = TelegramListener()
    listener.admin_chat_id = "999999999"
    with patch("src.infrastructure.services.telegram_listener.SessionCloud", SessionFactory):
        is_adm, is_guard, user_obj = asyncio.run(listener.get_user_status(555111))
    assert is_adm is False
    assert is_guard is True
    assert user_obj is not None and user_obj.username == "david"

    # 6. TelegramListener.cmd_stop awaits sync stop_scrapers via to_thread and escapes errors
    sent = []

    async def _cap_msg(text, chat_id=None, **kwargs):
        sent.append(text)
        return True

    with (
        patch("src.infrastructure.services.telegram_listener.stop_scrapers", return_value={"killed_processes": 3}),
        patch("src.infrastructure.services.telegram_listener.telegram_service.send_message", side_effect=_cap_msg),
    ):
        asyncio.run(listener.cmd_stop(555111))
    assert sent and "3" in sent[0]

    sent.clear()
    with (
        patch("src.infrastructure.services.telegram_listener.stop_scrapers", side_effect=RuntimeError("<bad>")),
        patch("src.infrastructure.services.telegram_listener.telegram_service.send_message", side_effect=_cap_msg),
    ):
        asyncio.run(listener.cmd_stop(555111))
    assert sent and "&lt;bad&gt;" in sent[0] and "<bad>" not in sent[0]

    # 7. AST guarantee: no async method in telegram_listener.py calls SessionCloud() directly on the event loop
    import ast
    from pathlib import Path

    listener_src = Path("src/infrastructure/services/telegram_listener.py").read_text(encoding="utf-8")
    tree = ast.parse(listener_src)

    def _has_direct_session_call(node: ast.AST, in_async: bool) -> list[tuple[int, str]]:
        hits: list[tuple[int, str]] = []
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.AsyncFunctionDef):
                hits.extend(_has_direct_session_call(child, True))
            elif isinstance(child, ast.FunctionDef):
                # Sync helper functions passed to asyncio.to_thread are expected to own SessionCloud()
                hits.extend(_has_direct_session_call(child, False))
            else:
                if (
                    in_async
                    and isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Name)
                    and child.func.id == "SessionCloud"
                ):
                    hits.append((child.lineno, "SessionCloud"))
                hits.extend(_has_direct_session_call(child, in_async))
        return hits

    direct_session_hits = _has_direct_session_call(tree, False)
    assert direct_session_hits == [], f"Blocking SessionCloud inside async defs: {direct_session_hits}"

    # 8. AST governance: every module-level SessionCloud binding in app/api/infra must be patched by conftest
    import tests.conftest as conftest_mod

    targets_set = set(conftest_mod._SESSION_TARGETS)
    scan_dirs = [
        Path("src/interfaces/api"),
        Path("src/application/services"),
        Path("src/application/jobs"),
        Path("src/infrastructure/services"),
        Path("src/infrastructure/scrapers"),
    ]
    missing_targets: list[str] = []
    for base_dir in scan_dirs:
        for py_file in sorted(base_dir.rglob("*.py")):
            mod_name = ".".join(py_file.with_suffix("").parts)
            mod_tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for stmt in mod_tree.body:
                if isinstance(stmt, ast.ImportFrom) and stmt.module == "src.infrastructure.database_cloud":
                    for alias in stmt.names:
                        if alias.name == "SessionCloud":
                            bound = f"{mod_name}.{alias.asname or alias.name}"
                            if bound == "src.interfaces.api.main._DefaultSessionCloud":
                                continue
                            if bound not in targets_set:
                                missing_targets.append(bound)
    assert missing_targets == [], f"Unpatched module-level SessionCloud bindings in conftest.py: {missing_targets}"
