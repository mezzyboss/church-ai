# Church Service Agent

A local-first, modular agent that automates church service production. It runs primarily on a Windows production computer.

## Architecture

```
main.py            entry point (settings + logging, then runs the workflow)
settings.py        env-var configuration (.env supported)
logging_config.py  Python logging (console + rotating file in logs/)
agents/            LangGraph agent (agent.py) and state (state.py)
workflows/         LangGraph graph definition (workflow.py)
tools/             StreamYard (Playwright) and browser setup; future ProPresenter tools
models/            Pydantic models: ServiceEvent, StreamConfig, SermonInfo
configs/ docs/ scripts/ tests/ logs/
```

Most functionality is currently **stubbed with TODOs** (`NotImplementedError`); only configuration, logging, models, Edge launch and the workflow skeleton exist.

## Local development

```
cd church-service-agent
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
playwright install msedge   # or install Microsoft Edge normally
copy .env.example .env
python main.py
pytest
```

## StreamYard automation

`tools/browser.py` launches Microsoft Edge via Playwright (`channel="msedge"`) with a persistent profile so the StreamYard login is reused. `tools/streamyard.py` defines `open_dashboard()`, `create_stream(title, description, date)` and `list_streams()` (TODO).

## ProPresenter automation

Planned: control ProPresenter through its network API / OSC, falling back to Windows UI automation where needed. Host/port are configured via `PROPRESENTER_HOST`/`PROPRESENTER_PORT`.

## Ollama integration

Planned: local LLMs via Ollama (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`) used by the agent for planning and content generation, keeping data on-premises.

## Roadmap

1. Implement StreamYard flows (dashboard, create, list).
2. ProPresenter integration.
3. Ollama-backed planning in the LangGraph workflow.
4. Scheduling, retries, human-in-the-loop approvals, richer observability.
