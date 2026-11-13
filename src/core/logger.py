import sys
import re
import logging
from loguru import logger
from src.core.config import settings

_SENSITIVE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"([?&](?:api_key|key|token|access_token|reset_token)=)[^&\s\"'<>]+", re.IGNORECASE), r"\1[REDACTED]"),
    (re.compile(r"(bot\d+:)[A-Za-z0-9_-]{12,}", re.IGNORECASE), r"\1[REDACTED]"),
    (re.compile(r"(postgres(?:ql)?(?:\+[a-z0-9_]+)?://[^:\s/]+:)[^@\s/]+(@)", re.IGNORECASE), r"\1[REDACTED]\2"),
    (re.compile(r"(Bearer\s+)[A-Za-z0-9._-]{12,}", re.IGNORECASE), r"\1[REDACTED]"),
)


def redact_sensitive_text(text: str) -> str:
    """Scrub API keys, Telegram bot tokens, DB credentials, and bearer tokens from logs."""
    if not text:
        return text
    cleaned = str(text)
    for pattern, repl in _SENSITIVE_PATTERNS:
        cleaned = pattern.sub(repl, cleaned)
    return cleaned


def _redact_loguru_record(record) -> None:
    record["message"] = redact_sensitive_text(record.get("message", ""))

# Register SUCCESS level (25) for standard logging
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

logging.Logger.success = success

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    """Configures application logging with JSON formatting for observability."""
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    # Prevent httpx/httpcore from logging query-string API keys or bot URLs at INFO level
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger.remove()  # Remove default handler
    logger.configure(patcher=_redact_loguru_record)
    
    # Stdout handler (Human readable for Dev, JSON for Prod could be added via env)
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File handler (Rotation & Retention)
    logger.add(
        "logs/oraculo.log",
        rotation="10 MB",
        retention="1 month",
        level="INFO",
        compression="zip"
    )

    logger.info(f"Logging initialized. Level: {log_level}")

setup_logging()
