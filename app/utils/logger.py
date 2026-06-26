"""
AskMyBook — Logging Configuration

Provides a consistent, configurable logger for the entire application.
Log level is controlled via the LOG_LEVEL environment variable.
"""

import logging
import sys


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Create and return a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module).
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler with formatted output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Format: timestamp | level | module | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
