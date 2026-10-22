"""
Real integration & cohesion tests for Performance Work Unit 5 (WU-5):
- PERF-14: GET /api/dashboard/stats returns condition_breakdown and waves_completion
  in the same response (eliminating 4 full-table catalog/collection HTTP requests on Dashboard mount)
  and executes in <= 6 SQL SELECT queries total.
"""
from sqlalchemy import event

from tests.conftest import _TestSession
from src.domain.models import ProductModel, CollectionItemModel, OfferModel


def test_dashboard_stats_includes_condition_breakdown_and_waves_completion_in_bounded_queries(
    client, authorized_device_headers
):
    """
    Cohesion test:
    1. Seeds modern and vintage products across waves ('Origins', 'Cartoon Collection', 'Vintage')
       and user collection items with MOC / NEW / LOOSE conditions.
    2. Calls GET /api/dashboard/stats?user_id=1 while counting SQL SELECT queries.
    3. Verifies condition_breakdown and waves_completion are returned accurately and
       total SQL SELECT queries <= 6.
    """
    with _TestSession() as db:
        p1 = ProductModel(
            name="WU5 He-Man",
            figure_id="WU5-1",
            category="Masters of the Universe",
            sub_category="Origins Wave 1",
            is_vintage=False,
            retail_price=20.0,
            avg_market_price=30.0,
        )
        p2 = ProductModel(
            name="WU5 Skeletor",
            figure_id="WU5-2",
            category="Masters of the Universe",
            sub_category="Origins Wave 1",
            is_vintage=False,
            retail_price=20.0,
            avg_market_price=40.0,
        )
        p3 = ProductModel(
            name="WU5 Teela",
            figure_id="WU5-3",
            category="Masters of the Universe",
            sub_category="Origins Wave 1",
            is_vintage=False,
            retail_price=20.0,
            avg_market_price=25.0,
        )
        p4 = ProductModel(
            name="WU5 Vintage Man-At-Arms",
            figure_id="WU5-4",
            category="Masters of the Universe",
            sub_category="Vintage 1982",
            is_vintage=True,
            retail_price=10.0,
            avg_market_price=80.0,
        )
        db.add_all([p1, p2, p3, p4])
        db.flush()

        # User 1 owns p1 (MOC 10.0), p2 (Loose 8.0), and p4 (New 9.0); p3 is missing from Origins Wave 1
        db.add_all([
            CollectionItemModel(
                owner_id=1,
                product_id=p1.id,
                acquired=True,
                condition="MOC",
                grading=10.0,
                purchase_price=20.0,
            ),
            CollectionItemModel(
                owner_id=1,
                product_id=p2.id,
                acquired=True,
                condition="Loose",
                grading=8.0,
                purchase_price=15.0,
            ),
            CollectionItemModel(
                owner_id=1,
                product_id=p4.id,
                acquired=True,
                condition="New",
                grading=9.0,
                purchase_price=50.0,
            ),
        ])
        db.add(
            OfferModel(
                product_id=p1.id,
                shop_name="Amazon.es",
                price=24.0,
                url="https://amazon.es/wu5-p1",
                is_available=True,
                source_type="Retail",
            )
        )
        db.commit()

    # Warm up auth/device/logistics caches once so we measure get_dashboard_stats itself
    client.get("/api/dashboard/stats?user_id=1", headers=authorized_device_headers)

    with _TestSession() as db:
        engine = db.get_bind()
        select_queries = []

        def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                select_queries.append(statement)

        event.listen(engine, "before_cursor_execute", _before_cursor_execute)
        try:
            res = client.get("/api/dashboard/stats?user_id=1", headers=authorized_device_headers)
        finally:
            event.remove(engine, "before_cursor_execute", _before_cursor_execute)

    assert res.status_code == 200
    body = res.json()

    assert "condition_breakdown" in body, "Expected condition_breakdown in /api/dashboard/stats"
    assert "waves_completion" in body, "Expected waves_completion in /api/dashboard/stats"

    cond_by_name = {c["name"]: c for c in body["condition_breakdown"]}
    assert "MOC" in cond_by_name and cond_by_name["MOC"]["value"] >= 1
    assert "Loose" in cond_by_name and cond_by_name["Loose"]["value"] >= 1
    assert "New" in cond_by_name and cond_by_name["New"]["value"] >= 1

    waves_by_name = {w["name"]: w for w in body["waves_completion"]}
    assert "Origins Wave 1" in waves_by_name
    wave1 = waves_by_name["Origins Wave 1"]
    assert wave1["total"] == 3
    assert wave1["owned"] == 2
    assert round(wave1["percentage"], 1) == 66.7
    assert "WU5 Teela" in wave1["missing_names"]
    assert wave1["missing_count"] == 1
    assert wave1["isVintage"] is False

    assert len(select_queries) <= 6, (
        f"Expected <= 6 SELECT queries in GET /api/dashboard/stats, got {len(select_queries)}:\n"
        + "\n---\n".join(select_queries)
    )
