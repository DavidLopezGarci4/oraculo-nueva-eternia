
import json
import os
from sqlalchemy import create_engine, text
from src.core.config import settings
from loguru import logger

def cloud_backup():
    logger.info("--- 🛡️ OPERACIÓN RESCATE: Iniciando Backup Cloud ---")
    
    # Usar la URL directamente de settings (ya cargada desde .env)
    cloud_url = settings.SUPABASE_DATABASE_URL
    if not cloud_url:
        logger.error("Error: SUPABASE_DATABASE_URL no configurada.")
        return

    engine = create_engine(cloud_url)
    backup_dir = "backups/cloud"
    os.makedirs(backup_dir, exist_ok=True)

    tables_to_backup = [
        "collection_items",
        "pending_matches",
        "blackcluded_items",
        "users",
        "price_history",
        "offer_history"
    ]

    try:
        with engine.connect() as conn:
            # 1. Listar tablas disponibles para no fallar si cambian de nombre
            res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            existing_tables = [row[0] for row in res]
            logger.info(f"Tablas encontradas en Supabase: {existing_tables}")

            for table in tables_to_backup:
                if table in existing_tables:
                    logger.info(f"Realizando backup de tabla: {table}")
                    data_res = conn.execute(text(f"SELECT * FROM {table}"))
                    
                    # Convertir a lista de diccionarios
                    columns = data_res.keys()
                    rows = [dict(zip(columns, row)) for row in data_res]
                    
                    filepath = os.path.join(backup_dir, f"{table}.json")
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(rows, f, indent=4, default=str)
                    
                    logger.success(f"Rescatados {len(rows)} registros de {table} -> {filepath}")
                else:
                    logger.warning(f"La tabla '{table}' no existe en este proyecto de Supabase.")

    except Exception as e:
        logger.error(f"Error durante el backup: {e}")
    
    logger.info("--- ✅ Backup Finalizado ---")

if __name__ == "__main__":
    cloud_backup()
