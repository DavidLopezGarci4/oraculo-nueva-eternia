import logging
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, VintageProductModel, ProductModel, ProductAliasModel, OfferHistoryModel, PendingMatchModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("delete_fictional_vintage")

def delete_fictional_items():
    urls = [
        "https://es.wallapop.com/item/he-man-vintage-1982-completo-fictional-1",
        "https://www.ebay.es/itm/skeletor-vintage-1982-in-blister-fictional-2",
        "https://www.vinted.es/items/he-man-1984-loose-fictional-3",
        "https://es.wallapop.com/item/man-at-arms-vintage-1983-fictional-4"
    ]
    
    product_names = [
        "He-Man Vintage 1982 completo",
        "Skeletor vintage 1982 en blister",
        "He-Man 1984 Loose",
        "Man-At-Arms Vintage 1983 figura"
    ]
    
    with SessionCloud() as db:
        deleted_offers = 0
        deleted_pending = 0
        deleted_products = 0
        deleted_aliases = 0
        deleted_history = 0
        deleted_vintage = 0
        
        # 1. Delete from offers, pending, aliases, history by URL
        for url in urls:
            deleted_offers += db.query(OfferModel).filter(OfferModel.url == url).delete()
            deleted_pending += db.query(PendingMatchModel).filter(PendingMatchModel.url == url).delete()
            deleted_aliases += db.query(ProductAliasModel).filter(ProductAliasModel.source_url == url).delete()
            deleted_history += db.query(OfferHistoryModel).filter(OfferHistoryModel.offer_url == url).delete()

        # 2. Find and delete products by name
        for name in product_names:
            products = db.query(ProductModel).filter(ProductModel.name == name).all()
            for p in products:
                # Delete vintage product link
                deleted_vintage += db.query(VintageProductModel).filter(VintageProductModel.product_id == p.id).delete()
                # Delete references from collection_items if any
                db.delete(p)
                deleted_products += 1
                    
        db.commit()
        logger.info("Cleanup finished successfully!")
        logger.info(f"Deleted {deleted_offers} offers, {deleted_pending} pending matches, {deleted_products} products, {deleted_aliases} aliases, {deleted_history} history logs, and {deleted_vintage} vintage association entries.")

if __name__ == "__main__":
    delete_fictional_items()
