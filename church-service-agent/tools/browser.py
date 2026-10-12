"""Playwright setup that launches Microsoft Edge."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import BrowserContext, sync_playwright

from settings import Settings

logger = logging.getLogger(__name__)


@contextmanager
def launch_edge(settings: Settings) -> Iterator[BrowserContext]:
    """Launch Edge with a persistent profile (keeps StreamYard login across runs).

    Requires Microsoft Edge installed on the machine (channel="msedge").
    """
    settings.browser_user_data_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        logger.info("Launching Microsoft Edge (headless=%s)", settings.browser_headless)
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(settings.browser_user_data_dir),
            channel="msedge",
            headless=settings.browser_headless,
            slow_mo=settings.browser_slow_mo_ms,
        )
        try:
            yield context
        finally:
            context.close()
