from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel

def check_af411_data():
    with SessionCloud() as db:
        products = db.query(ProductModel).limit(10).all()
        print(f"{'ID':<5} | {'Name':<30} | {'MSRP':<8} | {'Avg':<8} | {'P25':<8} | {'Pop':<5}")
        print("-" * 75)
        for p in products:
            print(f"{p.id:<5} | {p.name[:30]:<30} | {p.retail_price:<8} | {p.avg_market_price:<8} | {p.p25_price:<8} | {p.popularity_score:<5}")

if __name__ == "__main__":
    check_af411_data()
