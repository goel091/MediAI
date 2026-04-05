"""
src/logger.py
─────────────────────────────────────────────
Centralized logging configuration for the
AI-Powered Disease Prediction System.
─────────────────────────────────────────────
"""

import logging
import os
from datetime import datetime

# ── Create logs directory if it doesn't exist ──
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ── Log file path with timestamp ──
LOG_FILE = os.path.join(
    LOG_DIR,
    f"disease_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger.

    Args:
        name (str): Name of the logger (usually __name__).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Format ──
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Console Handler (INFO and above) ──
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ── File Handler (DEBUG and above) ──
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
