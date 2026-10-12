"""StreamYard tool interface (stubs)."""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

from playwright.sync_api import BrowserContext

from settings import Settings

logger = logging.getLogger(__name__)

GOOGLE_EMAIL_ENV = "STREAMYARD_GOOGLE_EMAIL"
GOOGLE_PASSWORD_ENV = "STREAMYARD_GOOGLE_PASSWORD"
LOGIN_TIMEOUT_MS = 120_000


class StreamYardAuthError(RuntimeError):
    """Raised when the StreamYard session cannot be authenticated."""


class StreamYardTool:
    def __init__(self, context: BrowserContext, settings: Settings) -> None:
        self.context = context
        self.settings = settings

    @staticmethod
    def is_authenticated(page) -> bool:
        """Heuristic: not on a login URL and no "Continue with Google" button.

        TODO: use a stable dashboard element once verified on the live site.
        """
        url = page.url.lower()
        if any(m in url for m in ("/login", "/signin", "/sign-in")):
            return False
        return page.get_by_text("Continue with Google").count() == 0

    def _login_with_google(self, page, email: str, password: str) -> None:
        """Sign in via Google. 2FA/CAPTCHA must be completed manually."""
        page.get_by_text("Continue with Google").first.click()
        page.wait_for_url("**://accounts.google.com/**", timeout=LOGIN_TIMEOUT_MS)
        page.get_by_label("Email or phone").fill(email)
        page.get_by_role("button", name="Next").click()
        page.locator('input[type="password"]').fill(password, timeout=LOGIN_TIMEOUT_MS)
        page.get_by_role("button", name="Next").click()
        page.wait_for_url("**://streamyard.com/**", timeout=LOGIN_TIMEOUT_MS)
        page.wait_for_load_state("domcontentloaded")

    def open_dashboard(self):
        """Open StreamYard, using Google sign-in if the session is signed out.

        Credentials come from STREAMYARD_GOOGLE_EMAIL / STREAMYARD_GOOGLE_PASSWORD
        and are never logged. Returns the authenticated page.
        """
        page = self.context.pages[0] if self.context.pages else self.context.new_page()
        page.goto(self.settings.streamyard_url, wait_until="domcontentloaded", timeout=60_000)
        if self.is_authenticated(page):
            return page
        email = os.environ.get(GOOGLE_EMAIL_ENV)
        password = os.environ.get(GOOGLE_PASSWORD_ENV)
        if not email or not password:
            raise StreamYardAuthError(
                f"Not signed in; set {GOOGLE_EMAIL_ENV} and {GOOGLE_PASSWORD_ENV}."
            )
        logger.info("Session not signed in; attempting Google sign-in.")
        try:
            self._login_with_google(page, email, password)
        except Exception as exc:
            raise StreamYardAuthError("Google sign-in failed.") from exc
        if not self.is_authenticated(page):
            raise StreamYardAuthError("Still not authenticated after Google sign-in.")
        return page

    def create_stream(self, title: str, description: str, date: Optional[datetime]) -> str:
        """Create a (scheduled) broadcast and return its identifier/URL."""
        # TODO: drive the StreamYard "create broadcast" flow with Playwright.
        raise NotImplementedError

    def list_streams(self) -> list[dict]:
        """List upcoming/existing streams."""
        # TODO: scrape the dashboard broadcast list.
        raise NotImplementedError
