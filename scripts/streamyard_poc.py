import argparse
import logging
import os
import sys
from pathlib import Path


logger = logging.getLogger("streamyard_poc")


def main():
    parser = argparse.ArgumentParser(
        description="Open StreamYard in Microsoft Edge using an existing Edge profile."
    )
    parser.add_argument(
        "--user-data-dir",
        help="Path to the Edge user data directory; defaults to "
        "STREAMYARD_EDGE_USER_DATA_DIR.",
    )
    args = parser.parse_args()

    user_data_dir = args.user_data_dir or os.environ.get(
        "STREAMYARD_EDGE_USER_DATA_DIR"
    )
    if not user_data_dir:
        logger.error(
            "Set STREAMYARD_EDGE_USER_DATA_DIR or pass --user-data-dir "
            "with your existing Edge user data directory."
        )
        return 2

    profile_dir = Path(user_data_dir).expanduser()
    if not profile_dir.is_dir():
        logger.error("Edge user data directory does not exist: %s", profile_dir)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        logger.error(
            "Playwright is not installed. Install dependencies with "
            "'python -m pip install -r requirements.txt'."
        )
        return 2

    context = None
    try:
        with sync_playwright() as playwright:
            logger.info("Launching Microsoft Edge with the existing profile.")
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="msedge",
                headless=False,
            )
            logger.info("Microsoft Edge launched.")

            page = context.pages[0] if context.pages else context.new_page()
            logger.info("Opening StreamYard.")
            response = page.goto(
                "https://streamyard.com/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            if response and response.status >= 400:
                raise RuntimeError(
                    f"StreamYard returned HTTP {response.status}."
                )

            logger.info("StreamYard opened: %s", page.url)
            logger.info("Current page title: %s", page.title())
            input("StreamYard is open. Press Enter to close Edge (or Ctrl+C). ")
            logger.info("Close requested.")
    except KeyboardInterrupt:
        logger.info("Interrupted; closing Edge.")
    except EOFError:
        logger.info("Input closed; closing Edge.")
    except Exception:
        logger.exception(
            "Could not open StreamYard. Confirm Edge is installed and that no "
            "other Edge process is using this profile."
        )
        return 1
    finally:
        if context is not None:
            try:
                context.close()
                logger.info("Edge closed.")
            except Exception:
                logger.exception("Could not close the Edge context cleanly.")

    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )
    sys.exit(main())
