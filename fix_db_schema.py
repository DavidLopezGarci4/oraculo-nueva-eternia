from sqlalchemy import text
from src.infrastructure.database_cloud import SessionCloud, engine_cloud
from loguru import logger

def fix_users_table():
    """
    Añade las columnas de reseteo de contraseña si no existen.
    SQLAlchemy create_all() no añade columnas a tablas existentes.
    """
    commands = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP WITHOUT TIME ZONE;"
    ]
    
    with SessionCloud() as db:
        try:
            for cmd in commands:
                logger.info(f"Ejecutando: {cmd}")
                db.execute(text(cmd))
            db.commit()
            logger.info("✅ Columnas de seguridad añadidas con éxito.")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error al actualizar la tabla: {e}")

if __name__ == "__main__":
    fix_users_table()
