"""LangGraph workflow definition."""
from __future__ import annotations

from agents.agent import ServiceAgent
from agents.state import AgentState


def build_workflow(agent: ServiceAgent | None = None):
    """Build and compile the service workflow graph."""
    from langgraph.graph import END, StateGraph

    agent = agent or ServiceAgent()
    graph = StateGraph(AgentState)
    graph.add_node("plan", agent.plan)
    graph.add_node("setup_stream", agent.setup_stream)
    graph.add_node("setup_slides", agent.setup_slides)
    graph.set_entry_point("plan")
    graph.add_edge("plan", "setup_stream")
    graph.add_edge("setup_stream", "setup_slides")
    graph.add_edge("setup_slides", END)
    # TODO: add conditional edges, retries, and human-in-the-loop checkpoints.
    return graph.compile()
