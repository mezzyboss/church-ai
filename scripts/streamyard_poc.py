import argparse
import logging
import os
import sys
import tempfile
from pathlib import Path


logger = logging.getLogger("streamyard_poc")

STREAMYARD_URL = "https://streamyard.com/"
GOOGLE_EMAIL_ENV = "STREAMYARD_GOOGLE_EMAIL"
GOOGLE_PASSWORD_ENV = "STREAMYARD_GOOGLE_PASSWORD"
LOGIN_TIMEOUT_MS = 120_000


def is_login_page(url: str) -> bool:
    """Return True if the URL looks like a StreamYard sign-in page."""
    lowered = url.lower()
    return any(marker in lowered for marker in ("/login", "/signin", "/sign-in"))


def is_authenticated(page) -> bool:
    """Heuristically decide whether the StreamYard session is signed in.

    TODO: replace with a check for a stable dashboard element once verified
    against the live site.
    """
    if is_login_page(page.url):
        return False
    return page.get_by_text("Continue with Google").count() == 0


def login_with_google(page, email: str, password: str) -> bool:
    """Sign in to StreamYard via Google using credentials from the environment.

    Returns True when the session appears authenticated afterwards. Google may
    request 2FA or a CAPTCHA, which cannot be automated: the function waits up
    to LOGIN_TIMEOUT_MS for those to be completed manually in the open window.
    Credentials are never logged or stored.
    """
    logger.info("Edge session is not signed in; attempting Google sign-in.")
    page.get_by_text("Continue with Google").first.click()
    page.wait_for_url("**://accounts.google.com/**", timeout=LOGIN_TIMEOUT_MS)
    page.get_by_label("Email or phone").fill(email)
    page.get_by_role("button", name="Next").click()
    page.locator('input[type="password"]').fill(password, timeout=LOGIN_TIMEOUT_MS)
    page.get_by_role("button", name="Next").click()
    logger.info("Credentials submitted; complete any Google verification manually.")
    page.wait_for_url("**://streamyard.com/**", timeout=LOGIN_TIMEOUT_MS)
    page.wait_for_load_state("domcontentloaded")
    return is_authenticated(page)


def ensure_logged_in(page) -> bool:
    """Use the existing Edge session if signed in, else fall back to Google."""
    if is_authenticated(page):
        logger.info("Existing Edge session is authenticated.")
        return True
    email = os.environ.get(GOOGLE_EMAIL_ENV)
    password = os.environ.get(GOOGLE_PASSWORD_ENV)
    if not email or not password:
        logger.warning(
            "Not signed in and %s / %s are not set; sign in manually.",
            GOOGLE_EMAIL_ENV,
            GOOGLE_PASSWORD_ENV,
        )
        return False
    try:
        return login_with_google(page, email, password)
    except Exception:
        logger.exception("Google sign-in failed; sign in manually in the window.")
        return False


def smoke_test(timeout_ms: int = 60_000, headless: bool = False) -> int:
    """Read-only check: launch Edge, open StreamYard, verify it loads, log it.

    Uses a throwaway temporary profile (no existing profile, no sign-in) and
    never creates or modifies a stream. Returns 0 on success, 1 on failure,
    2 if Playwright is missing.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        logger.error(
            "Playwright is not installed. Install dependencies with "
            "'python -m pip install -r requirements-smoke.txt'."
        )
        return 2

    logger.info("SMOKE TEST: read-only; no stream will be created or modified.")
    try:
        with tempfile.TemporaryDirectory(prefix="streamyard-smoke-") as tmp:
            with sync_playwright() as playwright:
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=tmp,
                    channel="msedge",
                    headless=headless,
                )
                try:
                    logger.info("Microsoft Edge launched.")
                    page = context.pages[0] if context.pages else context.new_page()
                    response = page.goto(
                        STREAMYARD_URL,
                        wait_until="domcontentloaded",
                        timeout=timeout_ms,
                    )
                    status = response.status if response else None
                    if status is not None and status >= 400:
                        raise RuntimeError(f"StreamYard returned HTTP {status}.")
                    title = page.title()
                    if "streamyard" not in (page.url + " " + title).lower():
                        raise RuntimeError(
                            f"Unexpected page: url={page.url!r} title={title!r}"
                        )
                    logger.info(
                        "SMOKE TEST PASSED: url=%s title=%r http_status=%s",
                        page.url,
                        title,
                        status,
                    )
                finally:
                    context.close()
                    logger.info("Edge closed.")
    except Exception:
        logger.exception("SMOKE TEST FAILED.")
        return 1
    return 0


def _open_streamyard(profile_dir: Path, headless: bool, action):
    """Launch Edge on a dedicated profile, open StreamYard, run ``action(page)``.

    Returns the action's result. Raises on launch/navigation failure.
    """
    from playwright.sync_api import sync_playwright

    profile_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            channel="msedge",
            headless=headless,
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            response = page.goto(
                STREAMYARD_URL, wait_until="domcontentloaded", timeout=60_000
            )
            if response and response.status >= 400:
                raise RuntimeError(f"StreamYard returned HTTP {response.status}.")
            return action(page)
        finally:
            context.close()
            logger.info("Edge closed.")


def login_check(profile_dir: Path, headless: bool = False) -> int:
    """Read-only: report whether the saved profile is signed in to StreamYard.

    Never uses the credentials fallback and never creates or modifies a stream.
    Returns 0 if AUTHENTICATED, 3 if NOT AUTHENTICATED, 1 on error, 2 if
    Playwright is missing.
    """
    try:
        import playwright  # noqa: F401
    except ModuleNotFoundError:
        logger.error("Playwright is not installed; see requirements-smoke.txt.")
        return 2

    def check(page) -> bool:
        page.wait_for_load_state("load")
        logger.info("Page url=%s title=%r", page.url, page.title())
        return is_authenticated(page)

    logger.info("LOGIN CHECK: read-only; profile=%s", profile_dir)
    try:
        authenticated = _open_streamyard(profile_dir, headless, check)
    except Exception:
        logger.exception("LOGIN CHECK FAILED.")
        return 1
    if authenticated:
        logger.info("AUTHENTICATED")
        return 0
    logger.warning("NOT AUTHENTICATED. Run with --login-setup first.")
    return 3


def login_setup(profile_dir: Path) -> int:
    """Open StreamYard headed so the user can sign in by hand (incl. 2FA).

    The session is saved in the dedicated profile for later runs. No
    credentials are read, logged, or stored by this script.
    """
    try:
        import playwright  # noqa: F401
    except ModuleNotFoundError:
        logger.error("Playwright is not installed; see requirements-smoke.txt.")
        return 2

    def wait_for_user(page) -> bool:
        logger.info("Sign in to StreamYard in the Edge window (complete any 2FA).")
        try:
            input("When you see your StreamYard dashboard, press Enter here. ")
        except (EOFError, KeyboardInterrupt):
            logger.info("Setup interrupted.")
        logger.info("Page url=%s title=%r", page.url, page.title())
        return is_authenticated(page)

    logger.info("LOGIN SETUP: profile=%s", profile_dir)
    try:
        authenticated = _open_streamyard(profile_dir, False, wait_for_user)
    except Exception:
        logger.exception("LOGIN SETUP FAILED.")
        return 1
    if authenticated:
        logger.info("LOGIN SETUP DONE: session saved. Verify with --login-check.")
        return 0
    logger.warning("Still not signed in; session may not be saved. Try again.")
    return 3


def main():
    parser = argparse.ArgumentParser(
        description="Open StreamYard in Microsoft Edge using an existing Edge profile."
    )
    parser.add_argument(
        "--user-data-dir",
        help="Path to the Edge user data directory; defaults to "
        "STREAMYARD_EDGE_USER_DATA_DIR.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Safe dry run: launch Edge with a temporary profile, open "
        "StreamYard, verify it loads, log, and exit. No sign-in, no changes.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="With --smoke-test or --login-check, run Edge without a visible window.",
    )
    parser.add_argument(
        "--login-setup",
        action="store_true",
        help="Open StreamYard so you can sign in manually once; the session is "
        "saved in the --user-data-dir profile (created if missing).",
    )
    parser.add_argument(
        "--login-check",
        action="store_true",
        help="Read-only: log AUTHENTICATED / NOT AUTHENTICATED for the profile "
        "and exit. Honors --headless.",
    )
    args = parser.parse_args()

    if args.smoke_test:
        return smoke_test(headless=args.headless)

    if args.login_setup or args.login_check:
        raw_dir = args.user_data_dir or os.environ.get("STREAMYARD_EDGE_USER_DATA_DIR")
        if not raw_dir:
            logger.error(
                "Pass --user-data-dir (e.g. C:\\church-ai\\edge-profile) or set "
                "STREAMYARD_EDGE_USER_DATA_DIR."
            )
            return 2
        profile = Path(raw_dir).expanduser()
        if args.login_setup:
            return login_setup(profile)
        return login_check(profile, headless=args.headless)

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

    try:
        with sync_playwright() as playwright:
            context = None
            try:
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
                    STREAMYARD_URL,
                    wait_until="domcontentloaded",
                    timeout=60_000,
                )
                if response and response.status >= 400:
                    raise RuntimeError(
                        f"StreamYard returned HTTP {response.status}."
                    )

                logger.info("StreamYard opened: %s", page.url)
                if not ensure_logged_in(page):
                    logger.warning("StreamYard session is not authenticated.")
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
    except Exception:
        logger.exception(
            "Could not start Playwright. Confirm the installation is complete."
        )
        return 1

    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("streamyard_poc.log", encoding="utf-8"),
        ],
    )
    sys.exit(main())
