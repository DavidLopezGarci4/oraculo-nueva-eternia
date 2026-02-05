from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, OfferModel, UserModel
from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
from loguru import logger

def repair_scores():
    with SessionCloud() as db:
        # Default user location
        user_location = "ES"
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if user: user_location = user.location
        
        logger.info(f"Starting Opportunity Score Repair (User Location: {user_location})")
        
        # Get all active retail offers
        offers = db.query(OfferModel).filter(
            OfferModel.is_available == True,
            OfferModel.source_type == 'Retail',
            OfferModel.product_id.isnot(None)
        ).all()
        
        logger.info(f"Found {len(offers)} active retail offers to check.")
        
        updated_count = 0
        for o in offers:
            # Check if score needs update (we'll update all to be safe, or just ones at 0)
            is_wish = any(ci.owner_id == 1 and not ci.acquired for ci in o.product.collection_items)
            landed_p = LogisticsService.get_landing_price(o.price, o.shop_name, user_location)
            fresh_score = DealScorer.calculate_score(o.product, landed_p, is_wish)
            
            if o.opportunity_score != fresh_score:
                o.opportunity_score = fresh_score
                db.add(o)
                updated_count += 1
                if updated_count % 50 == 0:
                    logger.info(f"Progress: {updated_count} scores updated...")

        db.commit()
        logger.success(f"Repair Complete! Total updated scores: {updated_count}")

if __name__ == "__main__":
    repair_scores()
