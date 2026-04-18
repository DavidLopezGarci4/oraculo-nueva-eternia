
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel, CollectionItemModel
from sqlalchemy import func

def check_users():
    with SessionCloud() as db:
        print("--- User Count Check ---")
        users = db.query(UserModel).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            count = db.query(func.count(CollectionItemModel.id)).filter(CollectionItemModel.owner_id == u.id).scalar()
            print(f"User: {u.username} (ID: {u.id}) | Role: {u.role} | Items: {count}")

if __name__ == "__main__":
    check_users()
