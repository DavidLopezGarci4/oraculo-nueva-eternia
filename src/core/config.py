from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError
import sys
from loguru import logger

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "El Oráculo de Nueva Eternia"
    VERSION: str = "2.0.0"
    DEBUG: bool = False

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
    
    # Notifications (Telegram)
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    # Email (SMTP) - Phase 15 Recovery
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SMTP_FROM: str = "Oráculo de Nueva Eternia <notificaciones@eternia.com>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

# Streamlit Secrets Support (Priority)
try:
    import streamlit as st
    if st.secrets:
        # Override default env loading if secrets found in st.secrets
        # We can pass them to Settings as init arguments
        secrets_dict = {}
        for key in Settings.__annotations__.keys():
            if key in st.secrets:
                secrets_dict[key] = st.secrets[key]
        
        settings = Settings(**secrets_dict)
    else:
        settings = Settings()
except Exception:
    # Fallback to standard .env if not in streamlit context
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
