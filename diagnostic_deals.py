
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import CollectionItemModel, ProductModel, OfferModel

def audit_collection():
    with SessionCloud() as db:
        # Check all collections
        counts = db.query(CollectionItemModel.owner_id).all()
        print(f"Total collections items: {len(counts)}")
        from collections import Counter
        print(f"User distributions: {Counter([c[0] for c in counts])}")
        
        user_id = 2
        owned = db.query(CollectionItemModel.product_id).filter(CollectionItemModel.owner_id == user_id).all()
        owned_ids = [p[0] for p in owned]
        print(f"User {user_id} owns {len(owned_ids)} products: {owned_ids[:10]}...")
        
        # Test the top deals query
        offers = db.query(OfferModel)\
            .join(ProductModel)\
            .filter(
                OfferModel.is_available == True,
                OfferModel.product_id.notin_(owned_ids) if owned_ids else True
            )\
            .order_by(OfferModel.price.asc())\
            .limit(20)\
            .all()
        
        print(f"Top 20 deals found: {len(offers)}")
        for i, o in enumerate(offers):
            is_owned = o.product_id in owned_ids
            print(f"{i+1}. {o.product.name} ({o.shop_name}) - {o.price}€ - Owned: {is_owned}")

if __name__ == "__main__":
    audit_collection()
