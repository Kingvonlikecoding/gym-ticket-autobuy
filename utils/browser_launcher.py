import os
from typing import List, Optional

from playwright.sync_api import Browser, Playwright

from utils.logger import setup_logger

logger = setup_logger(__name__)

WINDOWS_CHANNEL_MAP = {
    "microsoft edge": "msedge",
    "google chrome": "chrome",
}


def _detect_windows_default_channel() -> Optional[str]:
    """Detect default browser on Windows and map to Playwright channel."""
    if os.name != "nt":
        return None

    try:
        import winreg  # pylint: disable=import-error

        user_choice_key = (
            r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
        )
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, user_choice_key) as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")

        prog_id_lower = str(prog_id).lower()
        if "edge" in prog_id_lower:
            return "msedge"
        if "chrome" in prog_id_lower:
            return "chrome"
    except Exception as exc:  # pragma: no cover - best effort detection
        logger.debug(f"Failed to detect default browser from registry: {exc}")

    return None


def _candidate_channels() -> List[str]:
    channels: List[str] = []
    env_channel = os.getenv("PLAYWRIGHT_BROWSER_CHANNEL", "").strip().lower()
    if env_channel:
        channels.append(env_channel)

    detected = _detect_windows_default_channel()
    if detected and detected not in channels:
        channels.append(detected)

    for fallback in WINDOWS_CHANNEL_MAP.values():
        if fallback not in channels:
            channels.append(fallback)

    return channels


def launch_browser(playwright: Playwright, *, headless: bool, slow_mo: int = 0) -> Browser:
    """Launch browser preferring installed system channels before bundled Chromium."""
    for channel in _candidate_channels():
        try:
            logger.info(f"Trying system browser channel: {channel}")
            return playwright.chromium.launch(
                headless=headless,
                channel=channel,
                slow_mo=slow_mo,
            )
        except Exception as exc:
            logger.warning(f"Channel {channel} unavailable, trying next: {exc}")

    logger.warning("No system Chromium channel available, fallback to bundled browser.")
    return playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
