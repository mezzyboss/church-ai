"""Application configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is optional at import time
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    environment: str
    log_level: str
    log_dir: Path
    streamyard_url: str
    browser_headless: bool
    browser_user_data_dir: Path
    browser_slow_mo_ms: int
    ollama_base_url: str
    ollama_model: str
    propresenter_host: str
    propresenter_port: int


def load_settings() -> Settings:
    """Build Settings from the environment (and a local .env file if present)."""
    if load_dotenv is not None:
        load_dotenv(BASE_DIR / ".env")
    return Settings(
        environment=os.getenv("ENVIRONMENT", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        log_dir=BASE_DIR / os.getenv("LOG_DIR", "logs"),
        streamyard_url=os.getenv("STREAMYARD_URL", "https://streamyard.com"),
        browser_headless=_bool("BROWSER_HEADLESS", False),
        browser_user_data_dir=BASE_DIR / os.getenv("BROWSER_USER_DATA_DIR", ".browser-profile"),
        browser_slow_mo_ms=int(os.getenv("BROWSER_SLOW_MO_MS", "0")),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
        propresenter_host=os.getenv("PROPRESENTER_HOST", "127.0.0.1"),
        propresenter_port=int(os.getenv("PROPRESENTER_PORT", "1025")),
    )
