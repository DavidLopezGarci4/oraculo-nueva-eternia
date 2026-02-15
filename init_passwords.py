from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import UserModel
from src.core.security import SecurityShield
from src.core.config import settings

def init_user_passwords():
    print("Initializing User Passwords in Cloud DB...")
    with SessionCloud() as db:
        users = db.query(UserModel).all()
        for user in users:
            # We'll use the ORACULO_API_KEY as the initial password
            temp_password = settings.ORACULO_API_KEY
            user.hashed_password = SecurityShield.hash_password(temp_password)
            print(f"Password initialized for: {user.username} (Email: {user.email})")
        db.commit()
    print("Sync Complete. Users can now login with the API Key as password.")

if __name__ == "__main__":
    init_user_passwords()
