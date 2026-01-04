import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.infrastructure.database import SessionLocal
from src.domain.models import UserModel
from src.core.security import hash_password

def reset_admin():
    db = SessionLocal()
    print("--- RESET ACCESO ADMIN ---")
    
    # 1. Eliminar admin anterior si existe (para asegurar el hash correcto)
    existing_admin = db.query(UserModel).filter(UserModel.username == "admin").first()
    if existing_admin:
        db.delete(existing_admin)
        db.commit()
        print("[OK] Admin anterior eliminado.")

    # 2. Crear nuevo admin con hash bcrypt
    admin = UserModel(
        username="admin",
        email="admin@eternia.es",
        hashed_password=hash_password("eternia2026"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    print("[OK] Admin creado exitosamente.")
    print(" >>> Login: admin")
    print(" >>> Pass:  eternia2026")
    
    db.close()

if __name__ == "__main__":
    reset_admin()
