import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("playwright", MagicMock())
sys.modules.setdefault("playwright.sync_api", MagicMock())

from tools import streamyard as sy


def _tool(url="https://streamyard.com/dash", google=0):
    page = MagicMock()
    page.url = url
    page.get_by_text.return_value.count.return_value = google
    ctx = MagicMock()
    ctx.pages = [page]
    settings = MagicMock(streamyard_url="https://streamyard.com")
    return sy.StreamYardTool(ctx, settings), page


def test_authenticated_returns_page():
    tool, page = _tool()
    assert tool.open_dashboard() is page


def test_missing_credentials_raises(monkeypatch):
    monkeypatch.delenv(sy.GOOGLE_EMAIL_ENV, raising=False)
    monkeypatch.delenv(sy.GOOGLE_PASSWORD_ENV, raising=False)
    tool, _ = _tool(url="https://streamyard.com/login")
    with pytest.raises(sy.StreamYardAuthError):
        tool.open_dashboard()


def test_google_login_failure_raises(monkeypatch):
    monkeypatch.setenv(sy.GOOGLE_EMAIL_ENV, "a@example.com")
    monkeypatch.setenv(sy.GOOGLE_PASSWORD_ENV, "pw")
    tool, _ = _tool(url="https://streamyard.com/login")
    monkeypatch.setattr(tool, "_login_with_google", MagicMock(side_effect=RuntimeError))
    with pytest.raises(sy.StreamYardAuthError):
        tool.open_dashboard()
