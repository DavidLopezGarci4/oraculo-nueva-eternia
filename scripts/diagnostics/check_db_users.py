from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel

def check_users():
    print("--- User Audit ---")
    with SessionCloud() as db:
        users = db.query(UserModel).all()
        for u in users:
            print(f"ID: {u.id} | Username: {u.username} | Email: {u.email} | Role: {u.role}")

if __name__ == "__main__":
    check_users()
