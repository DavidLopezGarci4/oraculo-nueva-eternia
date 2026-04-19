
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel, CollectionItemModel
from sqlalchemy import func

def debug_users():
    with SessionCloud() as db:
        users = db.query(UserModel).all()
        print(f"Total users found: {len(users)}")
        for u in users:
            count = db.query(CollectionItemModel).filter(CollectionItemModel.owner_id == u.id).count()
            print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}, Collection Size: {count}")

if __name__ == "__main__":
    debug_users()
