"""Entry point for the Church Service Agent."""
from __future__ import annotations

import logging

from logging_config import configure_logging
from settings import load_settings

logger = logging.getLogger(__name__)


def main() -> None:
    settings = load_settings()
    configure_logging(settings)
    logger.info("Church Service Agent starting (env=%s)", settings.environment)
    # TODO: build the workflow (workflows.workflow.build_workflow) and run it
    # for an upcoming ServiceEvent loaded from configs/.
    logger.info("No workflow wired up yet; exiting.")


if __name__ == "__main__":
    main()
