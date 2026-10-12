# Decision log

This log records only design choices evidenced by repository files. Where
intent is not explicit in the code or documentation, the reason is marked
**Reason not documented**.

## Separate standalone PoC and agent application entry points

- **Decision:** Keep the StreamYard PoC as a repository-root script and the
  agent scaffold under `church-service-agent/`.
- **Evidence:** `scripts/streamyard_poc.py` and
  `church-service-agent/main.py` each have their own entry point; the root and
  package README files document different run commands.
- **Reason:** Reason not documented.
- **Consequences:** The PoC and agent application have separate execution
  flows, settings, and dependency manifests. The agent does not currently call
  the PoC.

## Use Playwright with an existing persistent Edge profile for browser access

- **Decision:** Launch Microsoft Edge through Playwright's persistent browser
  context rather than creating a fresh unauthenticated browser context.
- **Evidence:** `scripts/streamyard_poc.py` and
  `church-service-agent/tools/browser.py` call
  `chromium.launch_persistent_context()` with `channel="msedge"`. The PoC
  accepts an existing Edge user-data directory. Its documentation states that
  the profile must already be signed in to reuse the session.
- **Reason:** Reusing the existing Edge profile to retain the StreamYard login
  is documented in the PoC README and browser tool docstring.
- **Consequences:** Microsoft Edge must be installed, and the profile must be
  available to Playwright and not already in use by another Edge process.
  Browser profile contents are sensitive local state and must not be committed.

## Configure the agent through environment variables and optional `.env`

- **Decision:** Store the agent's runtime configuration in a `Settings`
  dataclass populated from environment variables, with optional `.env` loading.
- **Evidence:** `church-service-agent/settings.py` defines the frozen
  `Settings` dataclass and calls `load_dotenv()` for the package-local `.env`
  when python-dotenv is available. `church-service-agent/.env.example` lists
  example variables.
- **Reason:** The `load_settings()` docstring describes environment and local
  `.env` loading; a further rationale is not documented.
- **Consequences:** Environment values override defaults at startup, while
  paths and defaults are currently defined in code. The standalone PoC has a
  separate profile-directory input.

## Represent service data with Pydantic models

- **Decision:** Define service, stream, and sermon data as Pydantic models.
- **Evidence:** `church-service-agent/models/schemas.py` defines
  `ServiceEvent`, `StreamConfig`, and `SermonInfo` as `BaseModel` subclasses.
- **Reason:** Reason not documented.
- **Consequences:** These validated data shapes are available to application
  code, but no current entry point loads or processes a service event.

## Define the intended workflow as a sequential LangGraph

- **Decision:** Represent the planned agent flow as plan, stream setup, then
  slide setup, ending after those nodes.
- **Evidence:** `church-service-agent/workflows/workflow.py` creates a
  `StateGraph`, registers those three nodes, and links them in that order.
- **Reason:** Reason not documented.
- **Consequences:** The graph describes intended sequencing, but it is not
  invoked from `main.py` and its node functions currently raise
  `NotImplementedError`. Conditional flow, retries, and approval checkpoints
  are TODOs.

## Use standard-library console and rotating-file logging in the agent

- **Decision:** Configure Python standard-library logging with a console
  handler and a rotating file handler.
- **Evidence:** `church-service-agent/logging_config.py` uses
  `logging.config.dictConfig`, `StreamHandler`, and `RotatingFileHandler`.
- **Reason:** The module docstring specifies standard-library logging; a reason
  for the console-plus-file arrangement is not documented.
- **Consequences:** Agent logs are emitted to the console and to
  `logs/church_service_agent.log` by default, with rotation configured in code.
