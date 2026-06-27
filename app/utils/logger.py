"""
Centralized logger for the entire application.
Logs all API calls, evaluations, errors to a rotating log file.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import LOG_DIR, LOG_FILE, LOG_LEVEL

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger with both file and console handlers.

    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Question generated successfully")
        logger.error("API call failed", exc_info=True)
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler — rotates at 5MB, keeps 3 backups
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # only warnings+ in console

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger