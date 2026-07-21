
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


def _add_column_if_missing_sqlite(session, table: str, ddl: str) -> None:
    """
    SQLite no soporta `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (a diferencia
    de Postgres), así que "columna duplicada" es el resultado ESPERADO en
    cualquier arranque salvo el primero — se ignora explícitamente. Cualquier
    otro error (permisos, tabla bloqueada, DB corrupta...) se re-lanza: antes
    (Fase AAA-2.4) un `except: pass` genérico también silenciaba esos fallos
    reales sin dejar rastro.
    """
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError

    try:
        session.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl};"))
    except OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise


def init_cloud_db():
    from src.domain.models import Base
    Base.metadata.create_all(bind=engine_cloud)

    from sqlalchemy import text

    try:
        with SessionCloud() as session:
            dialect = engine_cloud.url.drivername or ""
            if "postgresql" in dialect.lower():
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_public_showcase BOOLEAN DEFAULT FALSE;"))
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR;"))
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pc_image_path VARCHAR;"))
                session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mobile_image_path VARCHAR;"))
            else:
                _add_column_if_missing_sqlite(session, "users", "is_public_showcase BOOLEAN DEFAULT FALSE")
                _add_column_if_missing_sqlite(session, "users", "telegram_chat_id VARCHAR")
                _add_column_if_missing_sqlite(session, "users", "pc_image_path VARCHAR")
                _add_column_if_missing_sqlite(session, "users", "mobile_image_path VARCHAR")
            session.commit()
    except Exception as e:
        # Fase AAA-2.4: antes esto era `except: pass` (silenciaba TODO fallo de
        # arranque de BD, incluidos los reales). Ahora queda visible en logs;
        # no se re-lanza porque main.py::lifespan ya envuelve init_cloud_db()
        # en su propio try/except de arranque tolerante a fallos.
        logger.error(f"Cloud DB :: fallo al aplicar el esquema en el arranque: {e}")
