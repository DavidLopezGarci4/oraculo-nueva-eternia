from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import OfferModel, ProductModel, PendingMatchModel, BlackcludedItemModel
import logging

logging.basicConfig(level=logging.INFO)

def check_p2p_stats():
    with SessionCloud() as db:
        # Total P2P offers available in OfferModel (Linked or Unlinked)
        total_p2p = db.query(OfferModel).filter(
            OfferModel.source_type == 'Peer-to-Peer',
            OfferModel.is_available == True
        ).count()
        
        # Linked P2P offers
        linked_p2p = db.query(OfferModel).filter(
            OfferModel.source_type == 'Peer-to-Peer',
            OfferModel.is_available == True,
            OfferModel.product_id.isnot(None)
        ).count()
        
        # Unlinked P2P offers in OfferModel
        unlinked_p2p_offer = db.query(OfferModel).filter(
            OfferModel.source_type == 'Peer-to-Peer',
            OfferModel.is_available == True,
            OfferModel.product_id.is_(None)
        ).count()

        # Check PendingMatchModel (The true Purgatorio)
        pending_p2p = db.query(PendingMatchModel).filter(
            PendingMatchModel.shop_name.in_(['Ebay.es', 'Wallapop'])
        ).count()
        
        # Check BlackcludedItemModel (Explicitly discarded)
        blacklisted_p2p = db.query(BlackcludedItemModel).filter(
            BlackcludedItemModel.source_type == 'Peer-to-Peer'
        ).count()

        # Check if eBay items are accidentally 'Retail'
        ebay_as_retail = db.query(OfferModel).filter(
            OfferModel.shop_name == 'Ebay.es',
            OfferModel.source_type == 'Retail'
        ).count()

        print(f"--- P2P AUDIT EXTENDED v2 ---")
        print(f"Total Available P2P in DB (OfferModel): {total_p2p}")
        print(f"Linked P2P (In El Pabellón): {linked_p2p}")
        print(f"Unlinked P2P in OfferModel: {unlinked_p2p_offer}")
        print(f"Items in Purgatorio (PendingMatchModel) for P2P shops: {pending_p2p}")
        print(f"Items in Shadow List (BlackcludedItemModel - Discarded): {blacklisted_p2p}")
        print(f"Ebay items tagged as RETAIL (Possible error): {ebay_as_retail}")

if __name__ == "__main__":
    check_p2p_stats()

if __name__ == "__main__":
    check_p2p_stats()
