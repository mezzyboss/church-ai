"""StreamYard tool interface (stubs)."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from playwright.sync_api import BrowserContext

from settings import Settings

logger = logging.getLogger(__name__)


class StreamYardTool:
    def __init__(self, context: BrowserContext, settings: Settings) -> None:
        self.context = context
        self.settings = settings

    def open_dashboard(self) -> None:
        """Open the StreamYard dashboard in Edge."""
        # TODO: navigate to settings.streamyard_url and verify login state.
        raise NotImplementedError

    def create_stream(self, title: str, description: str, date: Optional[datetime]) -> str:
        """Create a (scheduled) broadcast and return its identifier/URL."""
        # TODO: drive the StreamYard "create broadcast" flow with Playwright.
        raise NotImplementedError

    def list_streams(self) -> list[dict]:
        """List upcoming/existing streams."""
        # TODO: scrape the dashboard broadcast list.
        raise NotImplementedError
