import logging
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, VintageProductModel, ProductModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fix_existing_vintage_offers")

def fix_vintage_offers():
    logger.info("Starting fix of existing vintage offers in Cloud DB...")
    
    test_items_data = {
        "https://es.wallapop.com/item/he-man-vintage-1982-completo-fictional-1": {
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/he-man-motu-original.jpg",
            "condition": "Loose",
            "grading": 7.5
        },
        "https://www.ebay.es/itm/skeletor-vintage-1982-in-blister-fictional-2": {
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/skeletor-motu-original.jpg",
            "condition": "MOC",
            "grading": 8.5
        },
        "https://www.vinted.es/items/he-man-1984-loose-fictional-3": {
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/he-man-motu-original.jpg",
            "condition": "Loose",
            "grading": 6.5
        },
        "https://es.wallapop.com/item/man-at-arms-vintage-1983-fictional-4": {
            "image_url": "https://www.actionfigure411.com/images/figures/thumbs/man-at-arms-original.jpg",
            "condition": "Loose",
            "grading": 8.0
        }
    }
    
    with SessionCloud() as db:
        fixed_count = 0
        
        # 1. Update the specific 4 seeded fictional test items
        for url, data in test_items_data.items():
            offer = db.query(OfferModel).filter(OfferModel.url == url).first()
            if offer:
                logger.info(f"Fixing fictional vintage offer: {url}")
                offer.is_vintage = True
                offer.condition = data["condition"]
                offer.grading = data["grading"]
                offer.image_url = data["image_url"]
                fixed_count += 1
            else:
                logger.warning(f"Could not find fictional offer for URL: {url}")
        
        # 2. General repair: For any active offer linked to a Product marked as vintage,
        # set is_vintage = True and default condition/grading if null
        vintage_product_ids = [p.product_id for p in db.query(VintageProductModel).all()]
        other_vintage_offers = db.query(OfferModel).filter(
            OfferModel.product_id.in_(vintage_product_ids),
            OfferModel.is_vintage == False
        ).all()
        
        for offer in other_vintage_offers:
            logger.info(f"Fixing general vintage offer: {offer.url} (Product ID: {offer.product_id})")
            offer.is_vintage = True
            if not offer.condition:
                product_name = offer.product.name if offer.product else ""
                offer.condition = "MOC" if "moc" in product_name.lower() or "caja" in product_name.lower() or "nuevo" in product_name.lower() else "Loose"
            if not offer.grading:
                offer.grading = 9.0 if offer.condition == "MOC" else 7.5
            fixed_count += 1
            
        db.commit()
        logger.info(f"Completed! Fixed/updated {fixed_count} vintage offers in total.")

if __name__ == "__main__":
    fix_vintage_offers()
