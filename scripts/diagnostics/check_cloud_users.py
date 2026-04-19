from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel, ProductModel, CollectionItemModel
from loguru import logger

def check_cloud_data():
    logger.info("Checking data in CLOUD DB...")
    with SessionCloud() as db:
        users = db.query(UserModel).all()
        print(f"--- Users ({len(users)}) ---")
        for u in users:
            print(f"ID: {u.id} | Username: {u.username} | Role: {u.role}")

        product_count = db.query(ProductModel).count()
        print(f"\n--- Products Count: {product_count} ---")

        collection_count = db.query(CollectionItemModel).count()
        print(f"--- Collection Items Count: {collection_count} ---")
        
        # Check specific user data (David ID 2)
        david_items = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == 2).count()
        print(f"--- David's Items (ID 2): {david_items} ---")

if __name__ == "__main__":
    check_cloud_data()
