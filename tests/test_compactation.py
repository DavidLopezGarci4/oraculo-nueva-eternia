import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models import Base, ProductModel, OfferModel, PriceHistoryModel, ProductMonthlyStatsModel
from src.application.services.maintenance_service import MaintenanceService

class TestDatabaseCompactation(unittest.TestCase):
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
        
    def test_compactation_logic(self):
        # 1. Crear productos de prueba
        # Producto 1: Se convertirá en "muerto" (todas las ofertas inactivas)
        product_dead = ProductModel(
            name="Skeletor Vintage",
            figure_id="dead-01",
            category="Masters of the Universe"
        )
        # Producto 2: Seguirá "vivo" (tiene oferta activa)
        product_live = ProductModel(
            name="He-Man Origins",
            figure_id="live-01",
            category="Masters of the Universe"
        )
        self.db.add(product_dead)
        self.db.add(product_live)
        self.db.commit()
        
        # 2. Crear ofertas e historiales
        # Mes cerrado: hace 90 días
        date_past = datetime.now(timezone.utc) - timedelta(days=90)
        date_recent = datetime.now(timezone.utc) - timedelta(days=10)
        
        # Oferta muerta 1 (P2P) con historial de precios para Skeletor
        offer_dead = OfferModel(
            product_id=product_dead.id,
            shop_name="Wallapop",
            price=20.0,
            url="https://wallapop.com/skeletor",
            is_available=False,
            source_type="Peer-to-Peer"
        )
        self.db.add(offer_dead)
        self.db.commit()
        
        # Historial de precios para Skeletor (precios: 10.0, 20.0, 30.0)
        h1 = PriceHistoryModel(offer_id=offer_dead.id, price=10.0, recorded_at=date_past)
        h2 = PriceHistoryModel(offer_id=offer_dead.id, price=20.0, recorded_at=date_past)
        h3 = PriceHistoryModel(offer_id=offer_dead.id, price=30.0, recorded_at=date_past)
        self.db.add_all([h1, h2, h3])
        self.db.commit()
        
        # Ofertas para He-Man (una activa, una inactiva antigua)
        offer_live_active = OfferModel(
            product_id=product_live.id,
            shop_name="Smyths Toys",
            price=25.0,
            url="https://smythstoys.com/heman",
            is_available=True,
            source_type="Retail"
        )
        offer_live_inactive = OfferModel(
            product_id=product_live.id,
            shop_name="Amazon.es",
            price=18.0,
            url="https://amazon.es/heman",
            is_available=False,
            source_type="Retail"
        )
        self.db.add_all([offer_live_active, offer_live_inactive])
        self.db.commit()
        
        # Historial para He-Man: un precio reciente (10 días) y otro antiguo (90 días)
        h_live_recent = PriceHistoryModel(offer_id=offer_live_active.id, price=25.0, recorded_at=date_recent)
        h_live_old = PriceHistoryModel(offer_id=offer_live_inactive.id, price=15.0, recorded_at=date_past)
        self.db.add_all([h_live_recent, h_live_old])
        self.db.commit()
        
        # 3. Ejecutar compactación
        stats = MaintenanceService.compact_database(self.db)
        
        # 4. Verificaciones
        # Verificación A: Estadísticas del producto muerto (Skeletor)
        # Precios: 10.0, 20.0, 30.0. Promedio: 20.0. Mediana: 20.0. Min: 10.0. Max: 30.0.
        skeletor_stats = self.db.query(ProductMonthlyStatsModel).filter(
            ProductMonthlyStatsModel.product_id == product_dead.id
        ).first()
        
        self.assertIsNotNone(skeletor_stats)
        self.assertEqual(skeletor_stats.year, date_past.year)
        self.assertEqual(skeletor_stats.month, date_past.month)
        self.assertEqual(skeletor_stats.source_type, "Peer-to-Peer")
        self.assertEqual(skeletor_stats.offers_count, 3)
        self.assertEqual(skeletor_stats.avg_price, 20.0)
        self.assertEqual(skeletor_stats.median_price, 20.0)
        self.assertEqual(skeletor_stats.min_price, 10.0)
        self.assertEqual(skeletor_stats.max_price, 30.0)
        
        # Verificación B: Purgas del producto muerto (Skeletor)
        # Como Skeletor no tiene ofertas activas, debe borrarse la oferta obsoleta
        skeletor_offers = self.db.query(OfferModel).filter(OfferModel.product_id == product_dead.id).all()
        self.assertEqual(len(skeletor_offers), 0)
        
        # Verificación C: Estadísticas y purgas del producto vivo (He-Man)
        # Debe tener 1 estadística consolidada para el mes de hace 90 días (el precio antiguo de 15.0)
        heman_stats = self.db.query(ProductMonthlyStatsModel).filter(
            ProductMonthlyStatsModel.product_id == product_live.id,
            ProductMonthlyStatsModel.year == date_past.year,
            ProductMonthlyStatsModel.month == date_past.month
        ).first()
        self.assertIsNotNone(heman_stats)
        self.assertEqual(heman_stats.avg_price, 15.0)
        self.assertEqual(heman_stats.offers_count, 1)
        
        # Debe conservar las ofertas asociadas al producto vivo (incluso la inactiva ya que el producto está vivo)
        heman_offers = self.db.query(OfferModel).filter(OfferModel.product_id == product_live.id).all()
        self.assertEqual(len(heman_offers), 2)
        
        # Debe conservar el historial reciente de hace 10 días, pero purgar el antiguo de hace 90 días
        heman_history_recent = self.db.query(PriceHistoryModel).filter(
            PriceHistoryModel.recorded_at == date_recent
        ).all()
        self.assertEqual(len(heman_history_recent), 1)
        
        heman_history_old = self.db.query(PriceHistoryModel).filter(
            PriceHistoryModel.recorded_at == date_past,
            PriceHistoryModel.offer_id == offer_live_inactive.id
        ).all()
        self.assertEqual(len(heman_history_old), 0) # Purgado!

        print(">> PRUEBAS UNITARIAS DE COMPACTACIÓN FINOPS COMPLETADAS CON ÉXITO")

if __name__ == "__main__":
    unittest.main()
