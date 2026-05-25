import json
import random
from datetime import datetime, timezone
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import PendingMatchModel, ProductModel, VintageProductModel, OfferModel, OfferHistoryModel, ProductAliasModel
from src.core.vintage_utils import check_is_vintage
from src.infrastructure.repositories.product import ProductRepository
from src.application.services.logistics_service import LogisticsService
from src.application.services.deal_scorer import DealScorer
from loguru import logger

def migrate_existing_vintage():
    logger.info("Starting Purgatory Vintage Migration...")
    
    with SessionCloud() as db:
        repo = ProductRepository(db)
        # Fetch all pending items that are vintage
        pending_items = db.query(PendingMatchModel).all()
        
        migrated_count = 0
        for item in pending_items:
            is_v = check_is_vintage(item.scraped_name) or bool(item.is_vintage)
            if is_v:
                logger.info(f"Migrating vintage item: {item.scraped_name} ({item.shop_name})")
                
                # Find or create product
                product = db.query(ProductModel).filter(ProductModel.name == item.scraped_name).first()
                if not product:
                    rand_id = f"VINT-{random.randint(1000, 9999)}"
                    product = ProductModel(
                        name=item.scraped_name,
                        ean=item.ean,
                        image_url=item.image_url,
                        category="Masters of the Universe",
                        sub_category="Vintage",
                        is_vintage=True,
                        figure_id=rand_id
                    )
                    db.add(product)
                    db.flush()
                else:
                    product.is_vintage = True
                
                # Register in vintage_products
                exists_v = db.query(VintageProductModel).filter(VintageProductModel.product_id == product.id).first()
                if not exists_v:
                    v_prod = VintageProductModel(
                        product_id=product.id,
                        notes=f"Migrado automáticamente desde Purgatorio para {item.shop_name}"
                    )
                    db.add(v_prod)
                
                # Calculate score
                user_location = "ES"
                landed_p = LogisticsService.get_landing_price(item.price, item.shop_name, user_location)
                is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in product.collection_items)
                fresh_score = DealScorer.calculate_score(product, landed_p, is_wish)
                
                cond = item.condition or ("MOC" if "moc" in item.scraped_name.lower() or "caja" in item.scraped_name.lower() or "nuevo" in item.scraped_name.lower() else "Loose")
                grad = item.grading or (9.0 if cond == "MOC" else 7.5)
                
                offer_data = {
                    "shop_name": item.shop_name,
                    "price": item.price,
                    "currency": item.currency,
                    "url": item.url,
                    "is_available": True,
                    "source_type": item.source_type,
                    "receipt_id": item.receipt_id,
                    "opportunity_score": fresh_score,
                    "first_seen_at": item.found_at,
                    "last_price_update": datetime.now(timezone.utc),
                    "is_vintage": True,
                    "condition": cond,
                    "grading": grad,
                    "image_url": item.image_url,
                }
                
                repo.add_offer(product, offer_data, commit=False)
                
                # Audit
                history = OfferHistoryModel(
                    offer_url=item.url,
                    product_name=product.name,
                    shop_name=item.shop_name,
                    price=item.price,
                    action_type="LINKED_VINTAGE_MIGRATION",
                    details=json.dumps({"product_id": product.id, "receipt_id": item.receipt_id, "condition": cond, "grading": grad}),
                )
                db.add(history)
                
                # Alias
                db.query(ProductAliasModel).filter(ProductAliasModel.source_url == item.url).delete()
                new_alias = ProductAliasModel(product_id=product.id, source_url=item.url, confirmed=True)
                db.add(new_alias)
                
                # Remove from Purgatory
                db.delete(item)
                migrated_count += 1
                
        db.commit()
        logger.success(f"Successfully migrated {migrated_count} vintage items from Purgatory to Vintage Pabellón.")

if __name__ == "__main__":
    migrate_existing_vintage()
