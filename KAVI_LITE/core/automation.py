from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
import sys
import webbrowser

from config.settings import APP_COMMANDS, SCREENSHOT_DIR

try:
    import pyautogui
except ImportError:  # pragma: no cover - runtime optional
    pyautogui = None


def open_app(app_key: str) -> bool:
    command = APP_COMMANDS.get(app_key)
    if not command:
        return False

    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["cmd", "/c", "start", "", command], shell=False)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", command])
        else:
            subprocess.Popen([command])
        return True
    except OSError:
        return False


def open_website(url: str) -> bool:
    try:
        return webbrowser.open(url, new=2)
    except webbrowser.Error:
        return False


def google_search(query: str) -> bool:
    if not query:
        return False
    url = "https://www.google.com/search?q=" + query.replace(" ", "+")
    return open_website(url)


def take_screenshot() -> Path | None:
    if pyautogui is None:
        return None
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = SCREENSHOT_DIR / filename
    image = pyautogui.screenshot()
    image.save(path)
    return path
