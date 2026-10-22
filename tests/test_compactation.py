import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models import Base, ProductModel, OfferModel, PriceHistoryModel, ProductMonthlyStatsModel
from src.application.services.maintenance_service import MaintenanceService


class TestDatabaseCompactation(unittest.TestCase):
    def setUp(self):
        # Crear base de datos en memoria para pruebas
        self.engine = create_engine("sqlite:///:memory:")

        # Forzar activación de claves foráneas en SQLite para consistencia con Postgres
        from sqlalchemy import event

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_compactation_6_months_and_active_links_preservation(self):
        now = datetime.now(timezone.utc)
        # Hace 220 días (> 6 meses, mes cerrado)
        date_old_7m = now - timedelta(days=220)
        # Hace 90 días (3 meses, dentro de la ventana granular de 6 meses)
        date_mid_3m = now - timedelta(days=90)
        # Hace 10 días (dentro de 1 mes)
        date_recent_10d = now - timedelta(days=10)

        # Producto 1: Sin ofertas activas hoy, pero con una oferta inactiva de hace 7 meses y otra de hace 3 meses
        product_no_active = ProductModel(
            name="Skeletor Origins",
            figure_id="skel-01",
            category="Masters of the Universe",
            is_vintage=False,
        )
        # Producto 2: Con link activo antiguo (> 7 meses) y oferta inactiva antigua (> 7 meses)
        product_with_active = ProductModel(
            name="He-Man Origins",
            figure_id="heman-01",
            category="Masters of the Universe",
            is_vintage=False,
        )
        self.db.add_all([product_no_active, product_with_active])
        self.db.commit()

        # --- Ofertas para Producto 1 (Skeletor) ---
        # Oferta inactiva de hace 7 meses (> 6m -> debe compactarse y purgarse oferta + historial)
        offer_skel_old_dead = OfferModel(
            product_id=product_no_active.id,
            shop_name="Wallapop",
            price=20.0,
            url="https://wallapop.com/skeletor-old",
            is_available=False,
            source_type="Peer-to-Peer",
            first_seen_at=date_old_7m,
            last_seen=date_old_7m,
        )
        # Oferta inactiva de hace 3 meses (< 6m -> debe conservarse para gráficas de 3M y 6M)
        offer_skel_3m_inactive = OfferModel(
            product_id=product_no_active.id,
            shop_name="Vinted",
            price=24.0,
            url="https://vinted.es/skeletor-3m",
            is_available=False,
            source_type="Peer-to-Peer",
            first_seen_at=date_mid_3m,
            last_seen=date_mid_3m,
        )
        self.db.add_all([offer_skel_old_dead, offer_skel_3m_inactive])
        self.db.commit()

        # Historial hace 7 meses para Skeletor (10, 20, 30 -> avg 20, median 20, min 10, max 30)
        self.db.add_all([
            PriceHistoryModel(offer_id=offer_skel_old_dead.id, price=10.0, recorded_at=date_old_7m),
            PriceHistoryModel(offer_id=offer_skel_old_dead.id, price=20.0, recorded_at=date_old_7m),
            PriceHistoryModel(offer_id=offer_skel_old_dead.id, price=30.0, recorded_at=date_old_7m),
            PriceHistoryModel(offer_id=offer_skel_3m_inactive.id, price=24.0, recorded_at=date_mid_3m),
        ])
        self.db.commit()

        # --- Ofertas para Producto 2 (He-Man) ---
        # Oferta con LINK ACTIVO desde hace 7 meses (NO debe borrarse el link ni perder su referencia)
        offer_heman_active_long_lived = OfferModel(
            product_id=product_with_active.id,
            shop_name="Smyths Toys",
            price=25.0,
            url="https://smythstoys.com/heman-active",
            is_available=True,
            source_type="Retail",
            first_seen_at=date_old_7m,
            last_seen=date_recent_10d,
        )
        # Oferta inactiva de hace 7 meses en un producto vivo (DEBE purgarse al superar 6 meses inactiva)
        offer_heman_inactive_old = OfferModel(
            product_id=product_with_active.id,
            shop_name="Amazon.es",
            price=15.0,
            url="https://amazon.es/heman-dead",
            is_available=False,
            source_type="Retail",
            first_seen_at=date_old_7m,
            last_seen=date_old_7m,
        )
        self.db.add_all([offer_heman_active_long_lived, offer_heman_inactive_old])
        self.db.commit()

        self.db.add_all([
            PriceHistoryModel(offer_id=offer_heman_active_long_lived.id, price=23.0, recorded_at=date_old_7m),
            PriceHistoryModel(offer_id=offer_heman_active_long_lived.id, price=25.0, recorded_at=date_recent_10d),
            PriceHistoryModel(offer_id=offer_heman_inactive_old.id, price=15.0, recorded_at=date_old_7m),
        ])
        self.db.commit()

        # 3. Ejecutar compactación (Pasada 1)
        MaintenanceService.compact_database(self.db)

        # Verificación A: Estadísticas mensuales consolidadas de Skeletor (mes de hace 7m)
        skeletor_old_stats = self.db.query(ProductMonthlyStatsModel).filter(
            ProductMonthlyStatsModel.product_id == product_no_active.id,
            ProductMonthlyStatsModel.year == date_old_7m.year,
            ProductMonthlyStatsModel.month == date_old_7m.month,
        ).first()
        self.assertIsNotNone(skeletor_old_stats)
        self.assertEqual(skeletor_old_stats.source_type, "Peer-to-Peer")
        self.assertEqual(skeletor_old_stats.offers_count, 3)
        self.assertEqual(skeletor_old_stats.avg_price, 20.0)
        self.assertEqual(skeletor_old_stats.median_price, 20.0)
        self.assertEqual(skeletor_old_stats.min_price, 10.0)
        self.assertEqual(skeletor_old_stats.max_price, 30.0)

        # Verificación B: En Skeletor, la oferta inactiva de 7m se purga, pero la de 3m (< 6 meses) SE MANTIENE
        skeletor_remaining_offers = self.db.query(OfferModel).filter(
            OfferModel.product_id == product_no_active.id
        ).all()
        self.assertEqual(len(skeletor_remaining_offers), 1)
        self.assertEqual(skeletor_remaining_offers[0].url, "https://vinted.es/skeletor-3m")

        skeletor_remaining_history = self.db.query(PriceHistoryModel).join(OfferModel).filter(
            OfferModel.product_id == product_no_active.id
        ).all()
        self.assertEqual(len(skeletor_remaining_history), 1)
        self.assertEqual(skeletor_remaining_history[0].price, 24.0)

        # Verificación C: En He-Man, el link activo se MANTIENE intacto (sin purgar su historial activo) y la oferta muerta > 6m se purga
        heman_remaining_offers = self.db.query(OfferModel).filter(
            OfferModel.product_id == product_with_active.id
        ).all()
        self.assertEqual(len(heman_remaining_offers), 1)
        self.assertTrue(heman_remaining_offers[0].is_available)
        self.assertEqual(heman_remaining_offers[0].url, "https://smythstoys.com/heman-active")

        heman_active_history = self.db.query(PriceHistoryModel).filter(
            PriceHistoryModel.offer_id == offer_heman_active_long_lived.id
        ).all()
        self.assertEqual(len(heman_active_history), 2)

        # Verificación D: Re-ejecución idempotente (Pasada 2) NO sobrescribe ni degrada el mes ya compactado
        MaintenanceService.compact_database(self.db)
        heman_old_stats_after = self.db.query(ProductMonthlyStatsModel).filter(
            ProductMonthlyStatsModel.product_id == product_with_active.id,
            ProductMonthlyStatsModel.year == date_old_7m.year,
            ProductMonthlyStatsModel.month == date_old_7m.month,
        ).first()
        self.assertIsNotNone(heman_old_stats_after)
        self.assertEqual(heman_old_stats_after.offers_count, 2)
        self.assertEqual(heman_old_stats_after.avg_price, 19.0)


if __name__ == "__main__":
    unittest.main()
