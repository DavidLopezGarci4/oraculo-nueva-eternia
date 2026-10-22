import sqlite3
from sqlalchemy import create_engine, text, inspect
from src.core.config import settings
from src.domain.models import Base
import sys

def sync():
    """
    Migra los datos de oraculo.db (SQLite) a Supabase (Postgres).
    """
    print("🚀 Iniciando Sincronización Universal con Supabase...")
    
    # 1. Conexiones
    local_conn = sqlite3.connect("oraculo.db")
    local_conn.row_factory = sqlite3.Row
    
    cloud_url = settings.SUPABASE_DATABASE_URL
    if not cloud_url:
        print("❌ Error: SUPABASE_DATABASE_URL no está configurada en el .env")
        return

    cloud_engine = create_engine(cloud_url)
    
    # 2. Asegurar Esquema en Cloud
    print("📋 Asegurando que las tablas existen en la nube...")
    Base.metadata.create_all(bind=cloud_engine)
    
    # Lista de tablas a migrar en orden de dependencia
    # (Primero productos, luego ofertas/coleccion que dependen de ellos si hubiera FKs)
    tables = [
        "products",
        "offers",
        "price_history",
        "product_monthly_stats",
        "pending_matches",
        "collection",
        "price_alerts",
        "offer_history"
    ]
    
    try:
        with cloud_engine.begin() as cloud_conn:
            for table in tables:
                print(f"  -> Migrando tabla: {table}...")
                
                # Leer datos locales
                cursor = local_conn.cursor()
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                except sqlite3.OperationalError:
                    print(f"     ⚠️ Tabla {table} no existe en local, saltando.")
                    continue
                
                if not rows:
                    print(f"     ℹ️ Tabla {table} vacía en local.")
                    continue

                columns = rows[0].keys()
                placeholders = ", ".join([f":{col}" for col in columns])
                insert_stmt = text(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING")
                
                count = 0
                for row in rows:
                    cloud_conn.execute(insert_stmt, dict(row))
                    count += 1
                
                print(f"     ✅ {count} registros sincronizados.")

        print("\n✨ ¡Sincronización completada con éxito!")
        print("Ahora tu Oráculo vive en la nube.")

    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
    finally:
        local_conn.close()

if __name__ == "__main__":
    sync()
