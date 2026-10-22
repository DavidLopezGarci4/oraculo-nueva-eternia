import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models import (
    Base,
    ProductModel,
    OfferModel,
    PriceHistoryModel,
    ProductMonthlyStatsModel,
)
from src.application.services.market_analytics_service import MarketAnalyticsService


class TestMarketAnalyticsEMI(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_dynamic_periods_and_monthly_compacted_reuse_without_synthetic_sine(self):
        now = datetime.now(timezone.utc)
        date_8m = now - timedelta(days=240)
        date_4m = now - timedelta(days=120)
        date_20d = now - timedelta(days=20)
        date_2d = now - timedelta(days=2)

        prod = ProductModel(
            name="He-Man Origins",
            figure_id="heman-emi-1",
            category="Masters of the Universe",
            sub_category="Origins Core",
            retail_price=20.0,
            is_vintage=False,
        )
        self.db.add(prod)
        self.db.commit()

        # 1. Dato compactado mensual de hace 8 meses (> 6m, ya sin filas en price_history)
        monthly_stat_8m = ProductMonthlyStatsModel(
            product_id=prod.id,
            year=date_8m.year,
            month=date_8m.month,
            source_type="Peer-to-Peer",
            avg_price=16.0,
            median_price=16.0,
            min_price=15.0,
            max_price=17.0,
            p25_price=15.5,
            p75_price=16.5,
            std_dev_price=1.0,
            offers_count=5,
        )
        self.db.add(monthly_stat_8m)

        # 2. Oferta activa con historial en 4 meses (22€), 20 días (25€) y 2 días (30€)
        offer_active = OfferModel(
            product_id=prod.id,
            shop_name="Wallapop",
            price=30.0,
            url="https://wallapop.com/item/heman-emi",
            is_available=True,
            source_type="Peer-to-Peer",
            first_seen_at=date_4m,
            last_seen=date_2d,
        )
        self.db.add(offer_active)
        self.db.commit()

        self.db.add_all([
            PriceHistoryModel(offer_id=offer_active.id, price=22.0, recorded_at=date_4m),
            PriceHistoryModel(offer_id=offer_active.id, price=25.0, recorded_at=date_20d),
            PriceHistoryModel(offer_id=offer_active.id, price=30.0, recorded_at=date_2d),
        ])
        self.db.commit()

        # Consultar EMI en distintos periodos pasando la sesión de prueba
        res_1m = MarketAnalyticsService.get_market_index(period="1M", user_id=1, db_session=self.db)
        res_6m = MarketAnalyticsService.get_market_index(period="6M", user_id=1, db_session=self.db)
        res_1a = MarketAnalyticsService.get_market_index(period="1A", user_id=1, db_session=self.db)

        # A) Los periodos deben devolver metadatos dinámicos y series distintas adaptadas a cada horizonte
        self.assertIn("period_high", res_1m)
        self.assertIn("period_low", res_1m)
        self.assertIn("available_periods", res_1m)
        self.assertEqual(res_1m["available_periods"], ["1M", "3M", "6M", "1A", "ALL"])

        # B) En 1M, el precio inicial viene de ~22-25€ (arrastrado/observado hace 20-30d),
        # mientras que en 1A incorpora la estadística mensual compactada de hace 8 meses (16.0€)
        start_1m = res_1m["historical_series"][0]["index_value"]
        start_6m = res_6m["historical_series"][0]["index_value"]
        start_1a = res_1a["historical_series"][0]["index_value"]

        self.assertAlmostEqual(start_1a, 16.0, delta=1.0)
        self.assertGreater(start_6m, start_1a)
        self.assertNotEqual(res_1m["trend_pct"], res_1a["trend_pct"])

        # C) Verificar que NO hay oscilaciones sinusoidales artificiales:
        # Como los precios reales son monótonamente crecientes (16 -> 22 -> 25 -> 30),
        # la serie histórica de 1A debe ser monótonamente no decreciente.
        vals_1a = [pt["index_value"] for pt in res_1a["historical_series"]]
        for prev_v, next_v in zip(vals_1a, vals_1a[1:]):
            self.assertGreaterEqual(
                next_v,
                prev_v - 0.01,
                f"Se detectó caída artificial ({prev_v} -> {next_v}) por onda sintética en datos crecientes",
            )

    def test_compacted_only_product_contributes_to_emi_via_monthly_stats(self):
        now = datetime.now(timezone.utc)
        date_9m = now - timedelta(days=270)
        date_7m = now - timedelta(days=210)

        prod_compacted = ProductModel(
            name="Trap Jaw Origins",
            figure_id="trapjaw-emi-1",
            category="Masters of the Universe",
            sub_category="Origins Deluxe",
            retail_price=22.0,
            is_vintage=False,
        )
        self.db.add(prod_compacted)
        self.db.commit()

        self.db.add_all([
            ProductMonthlyStatsModel(
                product_id=prod_compacted.id,
                year=date_9m.year,
                month=date_9m.month,
                source_type="Peer-to-Peer",
                avg_price=28.0,
                median_price=28.0,
                min_price=26.0,
                max_price=30.0,
                p25_price=27.0,
                p75_price=29.0,
                std_dev_price=1.0,
                offers_count=4,
            ),
            ProductMonthlyStatsModel(
                product_id=prod_compacted.id,
                year=date_7m.year,
                month=date_7m.month,
                source_type="Peer-to-Peer",
                avg_price=35.0,
                median_price=35.0,
                min_price=33.0,
                max_price=37.0,
                p25_price=34.0,
                p75_price=36.0,
                std_dev_price=1.0,
                offers_count=6,
            ),
        ])
        self.db.commit()

        res_all = MarketAnalyticsService.get_market_index(period="ALL", user_id=1, db_session=self.db)
        self.assertEqual(res_all["current_index_value"], 35.0)
        self.assertEqual(res_all["historical_series"][0]["index_value"], 28.0)
        self.assertGreater(res_all["trend_pct"], 20.0)


if __name__ == "__main__":
    unittest.main()
