from unittest.mock import patch

from src.application.services.market_analytics_service import MarketAnalyticsService
from src.domain.models import (
    Base,
    CollectionItemModel,
    OfferModel,
    ProductModel,
    UserModel,
)
from tests.conftest import ADMIN_HEADERS, _TestSession


def test_composite_indexes_exist_on_hot_tables():
    """PERF-10: Verify composite indexes on offers, price_history, collection_items, and product_monthly_stats."""
    offers_idx = {idx.name for idx in Base.metadata.tables["offers"].indexes}
    ph_idx = {idx.name for idx in Base.metadata.tables["price_history"].indexes}
    coll_idx = {idx.name for idx in Base.metadata.tables["collection_items"].indexes}
    ms_idx = {idx.name for idx in Base.metadata.tables["product_monthly_stats"].indexes}

    assert "ix_offers_prod_avail_source" in offers_idx
    assert "ix_price_history_offer_rec" in ph_idx
    assert "ix_collection_owner_acq" in coll_idx
    assert "ix_monthly_stats_lookup" in ms_idx


def test_get_products_computes_best_p2p_price_and_source_without_selectinload_offers(client):
    """PERF-05: GET /api/products must return accurate best_p2p_price and best_p2p_source
    without hydrating all OfferModel ORM entities via selectinload(ProductModel.offers)."""
    with _TestSession() as db:
        prod = ProductModel(
            name="Skeletor WU3 P2P Test Figure",
            category="Action Figures",
            sub_category="Origins",
            figure_id="MOTU-WU3-P2P",
            is_vintage=False,
        )
        db.add(prod)
        db.flush()
        pid = prod.id

        db.add_all(
            [
                OfferModel(
                    product_id=pid,
                    shop_name="Amazon.es",
                    price=14.0,
                    url="https://example.com/wu3-retail",
                    source_type="Retail",
                    is_available=True,
                ),
                OfferModel(
                    product_id=pid,
                    shop_name="Ebay.es",
                    price=9.0,
                    url="https://example.com/wu3-p2p-sold",
                    source_type="Peer-to-Peer",
                    is_available=False,
                ),
                OfferModel(
                    product_id=pid,
                    shop_name="Vinted",
                    price=24.0,
                    url="https://example.com/wu3-p2p-vinted",
                    source_type="Peer-to-Peer",
                    is_available=True,
                ),
                OfferModel(
                    product_id=pid,
                    shop_name="Wallapop",
                    price=18.5,
                    url="https://example.com/wu3-p2p-walla",
                    source_type="Peer-to-Peer",
                    is_available=True,
                ),
            ]
        )
        db.commit()

    import inspect
    from src.interfaces.api.routers import products as products_router

    src_code = inspect.getsource(products_router.get_products)
    assert "selectinload(ProductModel.offers)" not in src_code, (
        "get_products must not eager-load all OfferModel ORM objects via selectinload(ProductModel.offers)"
    )

    res = client.get("/api/products?is_vintage=false&search=MOTU-WU3-P2P", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["best_p2p_price"] == 18.5
    assert items[0]["best_p2p_source"] == "Wallapop"


def test_market_index_caches_series_safely_per_user_and_preserves_null_is_vintage_offers():
    """PERF-03:
    1. Modern product offers with OfferModel.is_vintage=None must be included, while vintage product offers are excluded in SQL.
    2. Caching the market index series must NEVER leak User A's portfolio_metrics to User B.
    """
    if hasattr(MarketAnalyticsService, "invalidate_market_index_cache"):
        MarketAnalyticsService.invalidate_market_index_cache()

    with _TestSession() as db:
        u1 = UserModel(username="wu3_user_a", email="wu3_a@eternia.org", hashed_password="x", role="viewer")
        u2 = UserModel(username="wu3_user_b", email="wu3_b@eternia.org", hashed_password="x", role="viewer")
        db.add_all([u1, u2])
        db.flush()
        u1_id, u2_id = u1.id, u2.id

        mod_prod = ProductModel(
            name="Trap Jaw WU3 Modern",
            category="Action Figures",
            sub_category="Origins",
            figure_id="MOTU-WU3-MOD",
            is_vintage=False,
            retail_price=20.0,
        )
        vint_prod = ProductModel(
            name="He-Man 1982 WU3 Vintage",
            category="Action Figures",
            sub_category="Vintage",
            figure_id="MOTU-WU3-VINT",
            is_vintage=True,
            retail_price=20.0,
        )
        db.add_all([mod_prod, vint_prod])
        db.flush()

        # Offer on modern product with is_vintage=None (must be included!)
        db.add(
            OfferModel(
                product_id=mod_prod.id,
                shop_name="Wallapop",
                price=45.0,
                url="https://example.com/wu3-mod-null-vintage",
                source_type="Peer-to-Peer",
                is_available=True,
                is_vintage=None,
            )
        )
        # Expensive offer on vintage product (must be excluded in SQL!)
        db.add(
            OfferModel(
                product_id=vint_prod.id,
                shop_name="Ebay.es",
                price=900.0,
                url="https://example.com/wu3-vint-expensive",
                source_type="Peer-to-Peer",
                is_available=True,
                is_vintage=True,
            )
        )

        # User A owns mod_prod; User B owns nothing
        db.add(
            CollectionItemModel(
                product_id=mod_prod.id,
                owner_id=u1_id,
                acquired=True,
                purchase_price=15.0,
            )
        )
        db.commit()

    with patch("src.application.services.market_analytics_service.SessionCloud", _TestSession):
        res_a = MarketAnalyticsService.get_market_index(period="3M", user_id=u1_id)
        assert res_a["portfolio_metrics"] is not None
        assert res_a["portfolio_metrics"]["total_invested_eur"] == 15.0

        # Call for User B on the same period -> must hit series cache but compute User B's own portfolio_metrics (None)
        res_b = MarketAnalyticsService.get_market_index(period="3M", user_id=u2_id)
        assert res_b["portfolio_metrics"] is None, "User A's portfolio_metrics leaked to User B!"
        assert res_b["current_index_value"] == res_a["current_index_value"]
        assert res_b["current_index_value"] < 200.0, "Vintage 900€ offer leaked into modern market index!"
