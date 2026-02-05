from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, OfferModel

def check_products():
    with SessionCloud() as db:
        # Check some products from the previous offers
        product_ids = [1107, 936, 1168, 984, 1103]
        products = db.query(ProductModel).filter(ProductModel.id.in_(product_ids)).all()
        
        print(f"Checking {len(products)} products:")
        for p in products:
            print(f"Product {p.id}: {p.name}")
            print(f"  MSRP: {p.retail_price}")
            print(f"  P25: {p.p25_price}")
            print(f"  Score Vector: MSRP pts={p.retail_price if p.retail_price else 0}, P25 pts={p.p25_price if p.p25_price else 0}")

if __name__ == "__main__":
    check_products()
