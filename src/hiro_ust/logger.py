"""
Logging configuration for Hiro UST Generator.

Provides unified logging across the application with support for:
- Console output (INFO level)
- File logging (DEBUG level)
- Structured error reporting
"""

import logging
import sys
from pathlib import Path

# Create logger
logger = logging.getLogger("hiro_ust")
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers
if logger.hasHandlers():
    logger.handlers.clear()

# Console handler (INFO level)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(name)s [%(levelname)s]: %(message)s")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# File handler (DEBUG level) - optional
try:
    log_file = Path(__file__).parent.parent.parent / "logs" / "hiro_ust.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(name)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
except Exception:
    # If file logging fails, continue with console only
    pass


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"hiro_ust.{name}")
