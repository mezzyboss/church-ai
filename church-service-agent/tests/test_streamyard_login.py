import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import streamyard_poc as poc


def _page(url, google_buttons=0):
    page = MagicMock()
    page.url = url
    page.get_by_text.return_value.count.return_value = google_buttons
    return page


def test_is_login_page():
    assert poc.is_login_page("https://streamyard.com/login")
    assert not poc.is_login_page("https://streamyard.com/dashboard")


def test_authenticated_session_skips_google(monkeypatch):
    called = MagicMock()
    monkeypatch.setattr(poc, "login_with_google", called)
    assert poc.ensure_logged_in(_page("https://streamyard.com/x"))
    called.assert_not_called()


def test_unauthenticated_without_credentials(monkeypatch):
    monkeypatch.delenv(poc.GOOGLE_EMAIL_ENV, raising=False)
    monkeypatch.delenv(poc.GOOGLE_PASSWORD_ENV, raising=False)
    assert not poc.ensure_logged_in(_page("https://streamyard.com/login"))


def test_unauthenticated_falls_back_to_google(monkeypatch):
    monkeypatch.setenv(poc.GOOGLE_EMAIL_ENV, "a@example.com")
    monkeypatch.setenv(poc.GOOGLE_PASSWORD_ENV, "pw")
    login = MagicMock(return_value=True)
    monkeypatch.setattr(poc, "login_with_google", login)
    page = _page("https://streamyard.com/login")
    assert poc.ensure_logged_in(page)
    login.assert_called_once_with(page, "a@example.com", "pw")


def test_google_failure_returns_false(monkeypatch):
    monkeypatch.setenv(poc.GOOGLE_EMAIL_ENV, "a@example.com")
    monkeypatch.setenv(poc.GOOGLE_PASSWORD_ENV, "pw")
    monkeypatch.setattr(poc, "login_with_google", MagicMock(side_effect=RuntimeError))
    assert not poc.ensure_logged_in(_page("https://streamyard.com/login"))


def test_smoke_test_without_playwright(monkeypatch):
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)
    assert poc.smoke_test() == 2


def test_login_modes_without_playwright(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "playwright", None)
    assert poc.login_check(tmp_path) == 2
    assert poc.login_setup(tmp_path) == 2


def test_login_check_reports_status(monkeypatch, tmp_path):
    monkeypatch.setattr(poc, "_open_streamyard", lambda d, h, a: a(_page("https://streamyard.com/x")))
    assert poc.login_check(tmp_path) == 0
    monkeypatch.setattr(poc, "_open_streamyard", lambda d, h, a: a(_page("https://streamyard.com/login")))
    assert poc.login_check(tmp_path) == 3


def test_login_check_error(monkeypatch, tmp_path):
    def boom(*a):
        raise RuntimeError("x")
    monkeypatch.setattr(poc, "_open_streamyard", boom)
    assert poc.login_check(tmp_path) == 1
