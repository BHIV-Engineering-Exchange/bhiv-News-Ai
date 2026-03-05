"""
Structured logging configuration for News AI Backend
"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
from app.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry, default=str)


def setup_logging() -> None:
    """Setup structured logging configuration"""

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler with JSON formatter for production
    if settings.environment == "production":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)
    else:
        # Human-readable format for development
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("webdriver_manager").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, path: str, status_code: int, duration: float, client_ip: str = None):
    """Log HTTP request details"""
    extra_fields = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
        "client_ip": client_ip or "unknown"
    }

    if status_code >= 400:
        logger.warning(f"HTTP {method} {path} - {status_code}", extra={"extra_fields": extra_fields})
    else:
        logger.info(f"HTTP {method} {path} - {status_code}", extra={"extra_fields": extra_fields})


def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None):
    """Log error with context"""
    extra_fields = context or {}
    extra_fields["error_type"] = type(error).__name__
    extra_fields["error_message"] = str(error)

    logger.error(f"Error occurred: {str(error)}", extra={"extra_fields": extra_fields})