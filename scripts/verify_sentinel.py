import asyncio
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, PendingMatchModel, OfferModel
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from src.infrastructure.repositories.product import ProductRepository
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sentinel():
    with SessionCloud() as db:
        repo = ProductRepository(db)
        
        # 1. Crear un producto aislado para el test
        unique_id = str(uuid.uuid4())[:8]
        test_product_name = f"ORACULO-SENTINEL-{unique_id}"
        
        product = ProductModel(
            name=test_product_name,
            avg_market_price=100.0,
            category="Sentinel Test",
            figure_id=f"GUARD-{unique_id}"
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"Test Setup: Producto '{product.name}' (ID: {product.id}) configurado con Avg Price = 100.0 EUR")

        # 2. Simular Oferta con ANOMALÍA: 150 EUR (>40% de 100)
        anomaly_offer = {
            "product_name": test_product_name,
            "price": 150.0,
            "currency": "EUR",
            "url": f"https://eternia-hub.com/anomaly-{unique_id}",
            "shop_name": "Sentinel Test Shop",
            "image_url": "https://eternia-hub.com/img.jpg",
            "is_available": True,
            "source_type": "Retail"
        }

        # 3. Simular Oferta LEGÍTIMA: 110 EUR (<40% de 100)
        legit_offer = {
            "product_name": test_product_name,
            "price": 110.0,
            "currency": "EUR",
            "url": f"https://eternia-hub.com/legit-{unique_id}",
            "shop_name": "Sentinel Test Shop",
            "image_url": "https://eternia-hub.com/img.jpg",
            "is_available": True,
            "source_type": "Retail"
        }

        # 4. Procesar a través del Pipeline
        pipeline = ScrapingPipeline([])
        logger.info("Procesando ofertas a través del Pipeline con Sentinel activo...")
        pipeline.update_database([anomaly_offer, legit_offer])

        # 5. Verificar Resultados
        # El de 150 debería estar BLOQUEADO en Purgatorio
        purgatory_item = db.query(PendingMatchModel).filter(PendingMatchModel.url == anomaly_offer["url"]).first()
        if purgatory_item and purgatory_item.is_blocked:
            logger.info("✅ SUCCESS: Oferta de 150 EUR detectada como ANOMALÍA y BLOQUEADA en Purgatorio.")
            logger.info(f"   Flags: {purgatory_item.anomaly_flags}")
        else:
            logger.error("❌ FAILURE: La anomalía no fue bloqueada correctamente o no se encontró en Purgatorio.")

        # El de 110 debería estar VINCULADO como oferta activa
        active_offer = db.query(OfferModel).filter(OfferModel.url == legit_offer["url"]).first()
        if active_offer:
            logger.info("✅ SUCCESS: Oferta de 110 EUR vinculada normalmente.")
        else:
            logger.error("❌ FAILURE: La oferta legítima no fue vinculada.")

        # Limpieza
        if purgatory_item: db.delete(purgatory_item)
        if active_offer: db.delete(active_offer)
        db.delete(product)
        db.commit()
        logger.info("Limpieza de datos de prueba completada.")

if __name__ == "__main__":
    asyncio.run(test_sentinel())
