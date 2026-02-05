from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, OfferModel
from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService

def check_scoring():
    with SessionCloud() as db:
        user_location = "ES"
        # Check some products and their offers
        product_ids = [1107, 936, 1168, 984, 1103]
        for pid in product_ids:
            p = db.query(ProductModel).filter(ProductModel.id == pid).first()
            offers = db.query(OfferModel).filter(OfferModel.product_id == pid, OfferModel.is_available == True).all()
            
            print(f"\nProduct {p.id}: {p.name} (MSRP: {p.retail_price}, P25: {p.p25_price})")
            for o in offers:
                landed = LogisticsService.get_landing_price(o.price, o.shop_name, user_location)
                score = DealScorer.calculate_score(p, landed)
                print(f"  Offer {o.id} ({o.shop_name}): Price {o.price}, Landed {landed}, SCORE -> {score}")
                if o.opportunity_score != score:
                    print(f"    [!] DB Score {o.opportunity_score} DIFFERS from calculated {score}")

if __name__ == "__main__":
    check_scoring()
