import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

from app.settings import settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """

    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if hasattr(record, 'extra'):
            log_obj.update(record.extra)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging(
    name: Optional[str] = None,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration

    Args:
        name: Logger name (usually __name__)
        level: Logging level (defaults to settings.LOG_LEVEL)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name or __name__)

    # Set level
    log_level = getattr(logging, (level or settings.LOG_LEVEL).upper())
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Format based on debug mode
    if settings.DEBUG:
        # Detailed format for debugging
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # JSON format for production
        console_format = JSONFormatter()

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file or settings.LOGS_DIR:
        if log_file:
            file_path = Path(log_file)
        else:
            # Default log file
            timestamp = datetime.now().strftime("%Y%m%d")
            file_path = settings.LOGS_DIR / f"research_assistant_{timestamp}.log"

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return setup_logging(name)


# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)

# Configure specific loggers
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)