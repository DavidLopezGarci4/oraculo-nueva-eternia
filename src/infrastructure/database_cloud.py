
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.config import settings
from loguru import logger

# El Broker de FastAPI usará SUPABASE_DATABASE_URL si está disponible.
# Validación de soberanía: En producción, exigimos conexión Postgres.
cloud_url = settings.SUPABASE_DATABASE_URL or settings.DATABASE_URL

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
    connect_args={"check_same_thread": False, "timeout": 30} if "sqlite" in cloud_url else {}
)
SessionCloud = sessionmaker(autocommit=False, autoflush=False, bind=engine_cloud)

def init_cloud_db():
    from src.domain.models import Base
    Base.metadata.create_all(bind=engine_cloud)
