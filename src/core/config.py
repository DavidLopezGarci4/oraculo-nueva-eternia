from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError
import sys
import os
from loguru import logger
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from absolute project root .env
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "El Oráculo de Nueva Eternia"
    VERSION: str = "2.1.0-RECOVERY"
    DEBUG: bool = False
    # Deployment environment: "development" | "production".
    # In "production", insecure default secrets abort startup (see guard below).
    # Nombre "ENV" (no "ENVIRONMENT") para coincidir con la variable que ya
    # usan docker-compose.prod.yml y docker-compose.local-prod.yml.
    ENV: str = "development"

    # CORS allowed origins (comma-separated in .env, e.g. "https://oraculo-eternia.duckdns.org").
    CORS_ORIGINS: str = "http://localhost:3001,http://127.0.0.1:3001"

    # Database
    DATABASE_URL: str = "sqlite:///./oraculo.db"

    # External APIs (Optional for now, required for prod)
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None
    
    # Cloud Sync
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_DATABASE_URL: str | None = None
    ORACULO_API_KEY: str = "eternia-shield-2026" # Default key for dev
    
    # Sovereign Identity (Bypass Alias)
    SOVEREIGN_EMAIL: str | None = None
    
    # Notifications (Telegram)
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    # Email (SMTP) - Phase 15 Recovery
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SMTP_FROM: str = "Oráculo de Nueva Eternia <notificaciones@eternia.com>"

    # JWT - Phase 59
    JWT_SECRET: str = "oraculo-jwt-secret-CHANGE-IN-PRODUCTION"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Local Image Cache - Phase 68
    IMAGE_CACHE_DIR: str = "data/image_cache"

    # ScraperAPI Key
    SCRAPERAPI_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

# Fase AAA-2.4: se eliminó el soporte de "Streamlit Secrets" — streamlit no es
# una dependencia del proyecto (no está en requirements.txt ni se usa en
# ningún otro módulo), así que ese bloque SIEMPRE tomaba la rama de
# ImportError y caía al fallback. De paso, el `except Exception` genérico que
# lo envolvía dejaba inalcanzable el `except ValidationError` que debía hacer
# `sys.exit(1)` ante una configuración inválida: un error real de validación
# quedaba silenciado en vez de detener el arranque.
try:
    settings = Settings()
except ValidationError as e:
    logger.error(f"Configuration Error: {e}")
    sys.exit(1)

# Diagnostic Log for Shield and Alerts (No values leaked)
if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
    logger.info("📡 System Cloud: Telegram Alerts ENABLED.")
else:
    missing = []
    if not settings.TELEGRAM_BOT_TOKEN: missing.append("TOKEN")
    if not settings.TELEGRAM_CHAT_ID: missing.append("CHAT_ID")
    logger.warning(f"📡 System Cloud: Telegram Alerts DISABLED. Missing: {', '.join(missing)}")

if settings.SCRAPERAPI_KEY:
    os.environ["SCRAPERAPI_KEY"] = settings.SCRAPERAPI_KEY

# ─── Production secret guard (Phase AAA-1.5) ──────────────────────────────────
# Insecure default secrets are tolerated in development but MUST NOT reach
# production. If ENV=production and any critical secret still holds its
# example value, abort startup instead of silently exposing a known key.
_INSECURE_DEFAULTS = {
    "JWT_SECRET": "oraculo-jwt-secret-CHANGE-IN-PRODUCTION",
    "ORACULO_API_KEY": "eternia-shield-2026",
}
if settings.ENV.strip().lower() == "production":
    _leaked = [k for k, v in _INSECURE_DEFAULTS.items() if getattr(settings, k) == v]
    if _leaked:
        logger.critical(
            "FATAL: Insecure default value(s) in production for: "
            f"{', '.join(_leaked)}. Set strong secrets in .env "
            "(e.g. `python -c \"import secrets; print(secrets.token_urlsafe(48))\"`)."
        )
        sys.exit(1)


def get_cors_origins() -> list[str]:
    """Parse CORS_ORIGINS into a clean list of allowed origins."""
    return [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
