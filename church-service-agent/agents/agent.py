"""Service agent: node functions consumed by the LangGraph workflow."""
from __future__ import annotations

import logging

from agents.state import AgentState

logger = logging.getLogger(__name__)


class ServiceAgent:
    def plan(self, state: AgentState) -> AgentState:
        # TODO: use a local LLM (Ollama) to plan the service automation steps.
        raise NotImplementedError

    def setup_stream(self, state: AgentState) -> AgentState:
        # TODO: call StreamYardTool.create_stream for state["event"].
        raise NotImplementedError

    def setup_slides(self, state: AgentState) -> AgentState:
        # TODO: ProPresenter automation (OSC / API / Windows automation).
        raise NotImplementedError
