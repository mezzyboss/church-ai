import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models import ServiceEvent, SermonInfo, StreamConfig
from settings import load_settings


def test_models():
    e = ServiceEvent(
        name="Sunday", service_date=date(2026, 1, 4),
        stream=StreamConfig(title="t"), sermon=SermonInfo(title="s", speaker="p"),
    )
    assert e.stream.privacy == "public"


def test_settings_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("BROWSER_HEADLESS", "true")
    s = load_settings()
    assert s.log_level == "DEBUG" and s.browser_headless is True
