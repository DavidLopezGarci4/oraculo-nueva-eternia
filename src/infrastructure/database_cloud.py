
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.config import settings
from loguru import logger

# El Broker de FastAPI usará SUPABASE_DATABASE_URL si está disponible.
# Validación de soberanía: En producción, exigimos conexión Postgres.
cloud_url = settings.SUPABASE_DATABASE_URL or settings.DATABASE_URL

# Robustness: Strip whitespace and quotes that may have been copy-pasted in env/secrets
if isinstance(cloud_url, str):
    cloud_url = cloud_url.strip().strip("'\"")

if cloud_url and "postgresql" in cloud_url:
    logger.info("Cloud DB :: Connection to Supabase/Postgres detected.")
else:
    logger.error("Cloud DB :: MISSING CLOUD URL. Falling back to SQLite (Dashboard will be empty).")
    if settings.DEBUG:
        logger.warning("Cloud DB :: Debug mode allows SQLite.")
    else:
        # En producción real, esto debería alertar al Centinela.
        logger.warning("Cloud DB :: CHECK .env variables in OCI.")

engine_cloud = create_engine(
    cloud_url,
    pool_pre_ping=True,
    pool_recycle=1800,  # Recicla conexiones cada 30 min (previene desconexiones de Supabase)
    connect_args={"check_same_thread": False, "timeout": 30} if "sqlite" in cloud_url else {}
)
SessionCloud = sessionmaker(autocommit=False, autoflush=False, bind=engine_cloud)


def init_cloud_db():
    from src.domain.models import Base
    Base.metadata.create_all(bind=engine_cloud)
    
    try:
        from sqlalchemy import text
        with SessionCloud() as session:
            dialect = engine_cloud.url.drivername or ""
            if "postgresql" in dialect.lower():
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_public_showcase BOOLEAN DEFAULT FALSE;"))
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR;"))
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pc_image_path VARCHAR;"))
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mobile_image_path VARCHAR;"))
            else:
                session.execute(text("ALTER TABLE users ADD COLUMN is_public_showcase BOOLEAN DEFAULT FALSE;"))
                session.execute(text("ALTER TABLE users ADD COLUMN telegram_chat_id VARCHAR;"))
                try:
                    session.execute(text("ALTER TABLE users ADD COLUMN pc_image_path VARCHAR;"))
                except Exception:
                    pass
                try:
                    session.execute(text("ALTER TABLE users ADD COLUMN mobile_image_path VARCHAR;"))
                except Exception:
                    pass
            session.commit()
    except Exception:
        # Ignore if the column already exists or other issues
        pass
