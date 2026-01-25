
from src.infrastructure.database_cloud import SessionCloud
from src.application.services.market_intelligence import MarketIntelligenceService
from src.domain.models import ProductModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bulk_sync")

def bulk_sync():
    logger.info("Starting bulk synchronization of Market Intelligence stats...")
    with SessionCloud() as db:
        products = db.query(ProductModel).all()
        logger.info(f"Found {len(products)} products to sync.")
        
        service = MarketIntelligenceService(db)
        count = 0
        for p in products:
            try:
                service.sync_product_statistics(p.id)
                count += 1
                if count % 50 == 0:
                    logger.info(f"Synced {count} products...")
            except Exception as e:
                logger.error(f"Error syncing product {p.id}: {e}")
        
        logger.info(f"Bulk sync completed. {count} products updated.")

if __name__ == "__main__":
    bulk_sync()
