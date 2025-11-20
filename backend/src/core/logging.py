"""Logging configuration for the application."""

import logging

from src.config import settings


def setup_logging() -> None:
    """Configure application-wide logging settings."""
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
