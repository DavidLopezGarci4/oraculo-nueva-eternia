import os
from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
from src.domain.models import ProductModel, OfferModel, CollectionItemModel
from src.infrastructure.database_cloud import SessionCloud
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recovery_service")

def recover_and_normalize():
    print("--- ORACULO: CLOUD RESTORATION OPERATION ---")
    
    db = SessionCloud()
    try:
        offers = db.query(OfferModel).all()
        print(f"Processing {len(offers)} offers for normalization...")
        
        updated_count = 0
        for offer in offers:
            # 1. Normalize Category
            if offer.source_type and offer.source_type.lower() == 'retail':
                offer.source_type = 'Retail'
            elif offer.source_type and offer.source_type.lower() in ['peer-to-peer', 'p2p']:
                offer.source_type = 'Peer-to-Peer'
            
            # 2. Recalculate Opportunity Score with Landed Price
            # Default location ES for the analyst view
            landed_price = LogisticsService.get_landing_price(offer.price, offer.shop_name, "ES")
            
            # 3. Check Wishlist (Owner David ID 2)
            is_wish = db.query(CollectionItemModel).filter(
                CollectionItemModel.product_id == offer.product_id,
                CollectionItemModel.owner_id == 2,
                CollectionItemModel.acquired == False
            ).first() is not None
            
            if offer.product:
                print(f"  Item: {offer.product.name} | Price: {offer.price} | MSRP: {offer.product.retail_price} | P25: {offer.product.p25_price}")
                offer.opportunity_score = DealScorer.calculate_score(offer.product, landed_price, is_wish)
                if offer.opportunity_score > 0:
                     print(f"    -> SCORE: {offer.opportunity_score}")
                updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"  Progress: {updated_count}/{len(offers)}...")

        db.commit()
        print(f"SUCCESS: {updated_count} offers normalized and scored in Cloud.")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    recover_and_normalize()
