import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())
load_dotenv(override=True)

from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductMonthlyStatsModel, ProductModel

def check_db():
    print("Checking Supabase Production Database...")
    with SessionCloud() as db:
        try:
            total_stats = db.query(ProductMonthlyStatsModel).count()
            print(f"Total rows in product_monthly_stats: {total_stats}")
            
            if total_stats > 0:
                print("\nSample records:")
                samples = db.query(ProductMonthlyStatsModel).limit(5).all()
                for s in samples:
                    prod = db.query(ProductModel).filter(ProductModel.id == s.product_id).first()
                    p_name = prod.name if prod else "Unknown"
                    print(f" - Product: {p_name} | Date: {s.month:02d}/{s.year} | Channel: {s.source_type} | Avg Price: {s.avg_price} | Median Price: {s.median_price} | Count: {s.offers_count}")
            else:
                print("Table is empty.")
        except Exception as e:
            print(f"Error querying database: {e}")

if __name__ == "__main__":
    check_db()
