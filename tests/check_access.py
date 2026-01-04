import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.infrastructure.database import SessionLocal
from src.domain.models import UserModel
import hashlib

def check_users():
    db = SessionLocal()
    print("--- CONTROL DE ACCESO AL ORACULO ---")
    if not users:
        print("[!] No hay usuarios en la base de datos. Creando admin por defecto...")
        from src.core.security import hash_password
        
        admin = UserModel(
            username="admin",
            email="admin@eternia.es",
            hashed_password=hash_password("eternia2026"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("[OK] Usuario creado -> Login: admin / Pass: eternia2026")
    else:
        print(f"[OK] Usuarios encontrados: {len(users)}")
        for u in users:
            print(f"  - Usuario: {u.username} (Rol: {u.role})")
    
    db.close()

if __name__ == "__main__":
    check_users()
