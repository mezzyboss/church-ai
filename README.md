# church-ai

Automation for church service preparation and production.

## Current status

The repository contains a small, working StreamYard browser proof of concept
(PoC) and a separate Python agent application scaffold. The PoC opens StreamYard
in Microsoft Edge with an existing Edge profile and leaves the page open for
manual interaction; it does **not** create or schedule a broadcast.

The agent application currently loads settings, configures logging, and defines
domain models and a LangGraph workflow skeleton. Its `main.py` does not run the
workflow, and the agent and StreamYard operations are unfinished stubs. There
is no ProPresenter or Ollama integration.

## Repository structure

```text
.
├── README.md
├── requirements.txt                 # Dependencies used by the standalone PoC
├── scripts/
│   └── streamyard_poc.py             # Working manual StreamYard/Edge PoC
├── church-service-agent/
│   ├── main.py                       # Agent application entry point
│   ├── settings.py                   # Environment and optional .env settings
│   ├── logging_config.py             # Console and rotating-file logging
│   ├── agents/                       # Agent methods and workflow state
│   ├── workflows/                    # LangGraph workflow skeleton
│   ├── tools/                        # Edge launcher and StreamYard stubs
│   ├── models/                       # Pydantic service-domain models
│   ├── configs/                      # Currently contains usage guidance only
│   ├── tests/                        # Current unit tests
│   ├── docs/                         # Package documentation guidance
│   ├── scripts/                      # Package helper-script guidance
│   ├── .env.example
│   └── requirements.txt              # Agent application/test dependencies
└── docs/
    ├── architecture.md
    ├── current-state.md
    ├── decision-log.md
    └── roadmap.md
```

## Setup

Use Python 3.9 or newer, install Microsoft Edge, and work from the repository
root. The two `requirements.txt` files serve different entry points.

### Standalone StreamYard PoC

Install the root dependencies:

```sh
python -m pip install -r requirements.txt
```

In Edge, open `edge://version` and find **Profile path**. Use its parent
directory as the user data directory (for example, `.../User Data`, not
`.../User Data/Default`). Close Edge windows using that profile. The profile
must already be signed in to StreamYard.

Run the PoC by passing the user data directory:

```sh
python scripts/streamyard_poc.py --user-data-dir "/path/to/Edge/User Data"
```

Alternatively, set `STREAMYARD_EDGE_USER_DATA_DIR` and run
`python scripts/streamyard_poc.py` without the option. The script opens
StreamYard, waits for Enter (or Ctrl+C), and closes its Edge context. The
profile contains browser data: do not copy it into or commit it to this
repository.

### Agent application scaffold

Install its dependencies and run the entry point from the package directory:

```sh
cd church-service-agent
python -m pip install -r requirements.txt
python main.py
```

The command currently loads settings, initializes logging, reports that no
workflow is wired, and exits. Copy `.env.example` to `.env` in this directory
to customize the settings used by this application. Do not expect this entry
point to create a service or open StreamYard.

## Tests

From the repository root, install the agent requirements if they are not
already installed, then run:

```sh
python -m pip install -r church-service-agent/requirements.txt
python -m pytest church-service-agent/tests
```

The current tests cover basic Pydantic model defaults and environment-backed
settings. No lint or build configuration is present in the repository.

## Known limitations

- The standalone PoC is manual and only navigates to StreamYard; it does not
  create, schedule, or list broadcasts.
- The agent entry point does not invoke its workflow. Workflow nodes and
  StreamYard operations raise `NotImplementedError`.
- ProPresenter, Ollama-backed planning, service configuration files, retries,
  approvals, and end-to-end workflow behavior are not implemented.
- Tests do not cover browser automation, logging, the workflow, or the main
  entry point.
- The root and agent dependency manifests differ; see
  [Current state](docs/current-state.md).

## Immediate next development step

Implement and test the agent's StreamYard dashboard-opening operation, then
wire it into a runnable workflow only after its behavior and failure handling
are verified. This is the smallest step toward a usable service-creation path
without treating the current PoC as broadcast automation.

For the verified architecture, detailed current-state findings, repository
decisions, and planned phases, see [`docs/`](docs/).
