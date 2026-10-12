# Current state

This inventory is based on the repository code and configuration currently
present. A component described as implemented may still be disconnected from
the main application flow.

## What currently works

- `scripts/streamyard_poc.py` accepts an Edge user-data directory either as a
  command-line argument or through `STREAMYARD_EDGE_USER_DATA_DIR`. It launches
  a visible Edge persistent context, opens `https://streamyard.com/`, and waits
  for user input before closing.
- `church-service-agent/settings.py` builds a `Settings` object from
  environment variables and optionally a package-local `.env` file.
- `church-service-agent/logging_config.py` configures console and rotating-file
  logging.
- The Pydantic service, sermon, and stream models can be constructed, and the
  current tests exercise a model default and two environment settings.
- `church-service-agent/tools/browser.py` defines an Edge persistent-context
  lifecycle using configured browser settings. No current StreamYard operation
  calls it.

## What is partially implemented

- The agent application has an entry point, configuration, logging, models,
  state shape, browser context manager, and a graph definition, but the entry
  point does not invoke the graph.
- `build_workflow()` defines sequential plan, stream setup, and slide setup
  nodes. The graph is not usable end-to-end because all three agent node
  methods raise `NotImplementedError`.
- The standalone PoC demonstrates navigation to StreamYard but does not
  perform service preparation or broadcast creation.

## Stubs and TODOs

- `ServiceAgent.plan()`, `setup_stream()`, and `setup_slides()` are unimplemented.
- `StreamYardTool.open_dashboard()`, `create_stream()`, and `list_streams()` are
  unimplemented.
- `main.py` has a TODO to load an event from `configs/`, build the workflow, and
  run it.
- Workflow conditional edges, retries, and human-in-the-loop checkpoints are
  TODOs.
- ProPresenter automation and Ollama-backed planning have no implementation.
- `church-service-agent/configs/` contains only a README describing intended
  service/stream configuration files; no such files are present.

## Known technical issues and limitations

- There are two separate entry points: the standalone PoC and the agent
  scaffold. The latter does not call the former or share its command-line
  configuration.
- The root `requirements.txt` and
  `church-service-agent/requirements.txt` differ. The root manifest pins
  Playwright but leaves most other dependencies unpinned and includes
  LangChain, Ollama, and Rich. The package manifest uses version lower bounds,
  includes pytest, and marks Ollama as optional and commented out. There is no
  packaging or environment-management configuration to reconcile them.
- The PoC needs an existing Edge profile, and Edge must not already be using
  that profile. It does not verify whether the user is signed in beyond
  navigating and reporting the resulting page.
- The agent's StreamYard URL and browser profile settings are not used by the
  standalone PoC, which uses its own URL and profile input.
- The repository currently tracks a compiled Python bytecode file at
  `scripts/__pycache__/streamyard_poc.cpython-312.pyc`.

## Missing tests

There are only two basic tests, in `church-service-agent/tests/test_basics.py`.
There are no tests for:

- PoC argument handling, browser launch, navigation, or cleanup;
- browser/tool integration and StreamYard actions;
- workflow nodes, graph execution, or failure paths;
- application startup and logging configuration;
- configuration-file loading or end-to-end service preparation.

## Missing configuration

- No actual service-event YAML/JSON templates or input data are present.
- The standalone PoC's `STREAMYARD_EDGE_USER_DATA_DIR` is not listed in the
  package `.env.example`; it is documented at the root README instead.
- There is no shared configuration interface between the PoC and agent
  application.
- There is no formatter, linter, build, or CI/test workflow configuration in
  the inspected repository.

## Recommended next task

Implement and test `StreamYardTool.open_dashboard()` using the existing browser
context abstraction, including a clear check for an authenticated dashboard.
Then connect that operation to a runnable agent flow in a follow-up change.
This establishes a narrow, testable integration step before attempting
broadcast creation.
