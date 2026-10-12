"""Logging configuration using the standard library."""
from __future__ import annotations

import logging
import logging.config

from settings import Settings


def configure_logging(settings: Settings) -> None:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"default": {"format": fmt}},
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "default"},
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": str(settings.log_dir / "church_service_agent.log"),
                    "maxBytes": 5_000_000,
                    "backupCount": 5,
                    "encoding": "utf-8",
                },
            },
            "root": {"level": settings.log_level, "handlers": ["console", "file"]},
        }
    )
