"""LangGraph state definition."""
from __future__ import annotations

from typing import Optional, TypedDict

from models import ServiceEvent


class AgentState(TypedDict, total=False):
    event: ServiceEvent
    stream_id: Optional[str]
    messages: list[str]
    errors: list[str]
