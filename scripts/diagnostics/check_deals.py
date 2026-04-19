from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, ProductModel, CollectionItemModel
from datetime import datetime, timedelta

def check_deals():
    with SessionCloud() as db:
        user_id = 1
        owned_ids = [p[0] for p in db.query(CollectionItemModel.product_id).filter(CollectionItemModel.owner_id == user_id).all()]
        print(f"User {user_id} owns {len(owned_ids)} items.")
        
        freshness_threshold = datetime.utcnow() - timedelta(hours=72)
        print(f"Freshness threshold: {freshness_threshold}")
        
        offers = db.query(OfferModel).filter(
            OfferModel.is_available == True,
            OfferModel.source_type == 'Retail'
        ).all()
        
        print(f"Found {len(offers)} retail offers total.")
        
        fresh_offers = [o for o in offers if o.last_seen >= freshness_threshold]
        print(f"Found {len(fresh_offers)} fresh retail offers.")
        
        if fresh_offers:
            print("Sample fresh offers:")
            for o in fresh_offers[:5]:
                print(f"Offer {o.id}: Product {o.product_id}, Score {o.opportunity_score}, Last Seen {o.last_seen}")

        deals = [o for o in fresh_offers if o.opportunity_score > 0]
        print(f"Found {len(deals)} deals with score > 0.")
        
        if owned_ids:
            unowned_deals = [o for o in deals if o.product_id not in owned_ids]
            print(f"Found {len(unowned_deals)} unowned deals for user {user_id}.")

if __name__ == "__main__":
    check_deals()
