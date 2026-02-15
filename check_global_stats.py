from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import ProductModel, CollectionItemModel

def check_global_stats():
    print("--- Global Data Audit ---")
    with SessionCloud() as db:
        total_p = db.query(ProductModel).count()
        total_items = db.query(CollectionItemModel).count()
        print(f"Total Products in Nueva Eternia: {total_p}")
        print(f"Total Collection Items mapping: {total_items}")

if __name__ == "__main__":
    check_global_stats()
