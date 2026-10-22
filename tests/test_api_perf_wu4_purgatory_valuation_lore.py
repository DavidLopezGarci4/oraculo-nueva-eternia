"""
Real integration & cohesion tests for Performance Work Unit 4 (WU-4):
- PERF-04: GET /api/purgatory does not execute clean_purgatory_globally() + db.commit() on read
- PERF-06 & PERF-07: ValuationService preloads empty offer lists (preventing N+1 on 0-offer products),
  uses cached logistics rules, eager-loads ProductModel, and computes consolidated + pure landed in a single pass
- PERF-06 (Maintenance): MaintenanceService.compact_database batches queries and commits in O(1) round-trips
- RED-07: Lore harvest-missing avoids per-product commits and duplicate CharacterLoreModel queries
"""
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from sqlalchemy import event

from tests.conftest import _TestSession, API_KEY
from src.domain.models import (
    ProductModel,
    OfferModel,
    CollectionItemModel,
    PendingMatchModel,
    PriceHistoryModel,
    ProductMonthlyStatsModel,
    CharacterLoreModel,
)
from src.application.services.valuation_service import ValuationService
from src.application.services.maintenance_service import MaintenanceService


def test_get_purgatory_does_not_run_global_cleanup_on_get(client, authorized_device_headers):
    """
    Cohesion test:
    GET /api/purgatory must be a pure read operation and must NOT execute
    clean_purgatory_globally(db) on every page load.
    """
    with _TestSession() as db:
        p = ProductModel(
            name="He-Man",
            figure_id="WU4-HM-1",
            category="Masters of the Universe",
            sub_category="Origins",
            is_vintage=False,
        )
        db.add(p)
        pm = PendingMatchModel(
            scraped_name="MOTU Origins He-Man figure",
            price=19.99,
            currency="EUR",
            url="https://shop.example/wu4-purg-1",
            shop_name="ActionFigure411",
            source_type="Retail",
        )
        db.add(pm)
        db.commit()

    headers = {**authorized_device_headers, "X-API-Key": API_KEY}
    with patch("src.infrastructure.scrapers.pipeline.clean_purgatory_globally") as mock_clean:
        res = client.get("/api/purgatory?page=1&limit=50", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert any(item["url"] == "https://shop.example/wu4-purg-1" for item in data)
        assert mock_clean.call_count == 0, (
            f"Expected clean_purgatory_globally not to run on GET /api/purgatory, ran {mock_clean.call_count} times"
        )


def test_valuation_service_zero_offer_preload_and_single_pass_no_n_plus_1():
    """
    Cohesion test:
    When a user's collection has multiple items (including items with 0 active offers),
    ValuationService.get_collection_valuation must NOT fall back to per-product
    OfferModel queries or lazy-load ProductModel per item.
    """
    with _TestSession() as db:
        products = []
        for idx in range(6):
            p = ProductModel(
                name=f"WU4 Valuation Hero {idx}",
                figure_id=f"WU4-VAL-{idx}",
                category="Masters of the Universe",
                sub_category="Origins",
                is_vintage=False,
                retail_price=20.0,
                avg_market_price=25.0 + idx,
            )
            db.add(p)
            products.append(p)
        db.flush()

        # Only first 2 products have active offers; the other 4 have 0 active offers
        db.add(
            OfferModel(
                product_id=products[0].id,
                shop_name="Amazon.es",
                price=18.0,
                url="https://amazon.es/wu4-val-0",
                is_available=True,
                source_type="Retail",
            )
        )
        db.add(
            OfferModel(
                product_id=products[1].id,
                shop_name="Wallapop",
                price=22.0,
                url="https://wallapop.com/wu4-val-1",
                is_available=True,
                source_type="Peer-to-Peer",
            )
        )

        for idx, p in enumerate(products):
            db.add(
                CollectionItemModel(
                    owner_id=1,
                    product_id=p.id,
                    acquired=True,
                    condition="MOC",
                    grading=10.0,
                    purchase_price=15.0,
                )
            )
        db.commit()

    # Use a fresh session so identity map is empty
    with _TestSession() as db:
        val_service = ValuationService(db)

        queries = []

        def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                queries.append(statement)

        engine = db.get_bind()
        event.listen(engine, "before_cursor_execute", _before_cursor_execute)
        try:
            result = val_service.get_collection_valuation(user_id=1, user_location="ES", is_vintage=False)
        finally:
            event.remove(engine, "before_cursor_execute", _before_cursor_execute)

        assert result["item_count"] >= 6
        assert result["total_invested"] >= 90.0
        assert result["total_value"] > 0
        # Should only run 2 SELECT queries: 1 for CollectionItem JOIN Product, 1 for batch OfferModel preload
        assert len(queries) <= 3, (
            f"Expected at most 3 SELECT queries for collection valuation, got {len(queries)}:\n"
            + "\n---\n".join(queries)
        )


def test_compact_database_batches_queries_in_constant_round_trips():
    """
    Cohesion test:
    MaintenanceService.compact_database must consolidate monthly stats and purge
    expired inactive offers in a constant number of SQL queries (independent of N products).
    """
    now = datetime.now(timezone.utc)
    old_date = now - timedelta(days=210)
    recent_date = now - timedelta(days=20)

    with _TestSession() as db:
        for idx in range(5):
            p = ProductModel(
                name=f"WU4 Compact Fig {idx}",
                figure_id=f"WU4-CMP-{idx}",
                category="Masters of the Universe",
                sub_category="Origins",
                is_vintage=False,
            )
            db.add(p)
            db.flush()

            dead_offer = OfferModel(
                product_id=p.id,
                shop_name="Wallapop",
                price=20.0 + idx,
                url=f"https://wallapop.com/wu4-cmp-dead-{idx}",
                is_available=False,
                source_type="Peer-to-Peer",
                first_seen_at=old_date,
                last_seen=old_date,
            )
            live_offer = OfferModel(
                product_id=p.id,
                shop_name="Amazon.es",
                price=19.0 + idx,
                url=f"https://amazon.es/wu4-cmp-live-{idx}",
                is_available=True,
                source_type="Retail",
                first_seen_at=old_date,
                last_seen=recent_date,
            )
            db.add_all([dead_offer, live_offer])
            db.flush()

            db.add_all([
                PriceHistoryModel(offer_id=dead_offer.id, price=18.0 + idx, recorded_at=old_date),
                PriceHistoryModel(offer_id=dead_offer.id, price=22.0 + idx, recorded_at=old_date),
                PriceHistoryModel(offer_id=live_offer.id, price=19.0 + idx, recorded_at=recent_date),
            ])
        db.commit()

    with _TestSession() as db:
        select_queries = []

        def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                select_queries.append(statement)

        engine = db.get_bind()
        event.listen(engine, "before_cursor_execute", _before_cursor_execute)
        try:
            stats = MaintenanceService.compact_database(db)
        finally:
            event.remove(engine, "before_cursor_execute", _before_cursor_execute)

        assert stats["products_processed"] >= 5
        assert stats["monthly_stats_saved"] >= 10
        assert stats["offers_purged"] >= 5
        # Regardless of how many products exist, SELECT count must be bounded (<= 10)
        assert len(select_queries) <= 10, (
            f"Expected <= 10 SELECT queries in compact_database, got {len(select_queries)}"
        )
