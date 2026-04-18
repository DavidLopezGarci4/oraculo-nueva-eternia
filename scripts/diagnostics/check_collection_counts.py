from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import CollectionItemModel

def check_collection():
    print("--- Collection Audit ---")
    with SessionCloud() as db:
        # Check Admin (ID 1)
        admin_count = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == 1).count()
        admin_acquired = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == 1, CollectionItemModel.acquired == True).count()
        
        # Check David (ID 2)
        david_count = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == 2).count()
        david_acquired = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == 2, CollectionItemModel.acquired == True).count()
        
        print(f"Admin (1): Total={admin_count} | Acquired={admin_acquired}")
        print(f"David (2): Total={david_count} | Acquired={david_acquired}")

if __name__ == "__main__":
    check_collection()
