from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel
import logging

logging.basicConfig(level=logging.INFO)

def fix_ebay_tags():
    with SessionCloud() as db:
        updated = db.query(OfferModel).filter(
            OfferModel.shop_name == 'Ebay.es',
            OfferModel.source_type == 'Retail'
        ).update({OfferModel.source_type: 'Peer-to-Peer'}, synchronize_session=False)
        db.commit()
        print(f"Updated {updated} eBay offers to Peer-to-Peer")

if __name__ == "__main__":
    fix_ebay_tags()
