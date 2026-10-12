# Roadmap

The phases below describe planned work, not completed functionality. The
implemented pieces are called out separately so that the roadmap does not imply
that the overall capabilities already work.

## Phase 1: Reliable StreamYard browser automation

**Status: Partially demonstrated; reliable service automation is planned.**

- **Implemented:** A standalone Playwright PoC opens StreamYard in Microsoft
  Edge using an existing profile and leaves the page available for manual use.
- **Implemented (PoC only, unverified live):** Google sign-in fallback when
  the Edge session is unauthenticated, using environment credentials.
- **Implemented (mock-tested, unverified live):** `StreamYardTool.open_dashboard()`
  with login detection and Google fallback.
- **Planned:** Verify it live, then implement and test navigation and login-state
  detection in `StreamYardTool`.
- **Planned:** Implement broadcast creation and listing with explicit error
  handling, browser cleanup, and focused tests.
- **Planned:** Connect the StreamYard operations to the agent workflow.

## Phase 2: Configuration-driven service creation

**Status: Planned.**

- Add service configuration files and load a service event from `configs/`.
- Define how service, stream, and sermon model data maps to StreamYard actions.
- Validate configuration and test an end-to-end configured service flow.

## Phase 3: ProPresenter integration

**Status: Planned.**

- Implement an integration for slide setup. The agent stub names OSC, an API,
  or Windows automation as possible approaches; no approach is implemented or
  selected in the code.
- Connect the integration to the service workflow and cover it with tests.

## Phase 4: Agentic orchestration

**Status: Planned; only a non-operational LangGraph skeleton exists.**

- Implement agent planning; Ollama configuration values exist, but no Ollama
  client or LLM integration is implemented.
- Add workflow branching, retries, and human-in-the-loop checkpoints, which
  are TODOs in the current workflow module.
- Add the orchestration tests and observability needed for the implemented
  flow.
