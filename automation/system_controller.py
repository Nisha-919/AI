from __future__ import annotations

import os
import re
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

import requests

from memory.memory_manager import MemoryManager


class SystemController:
    def __init__(self, memory: MemoryManager, weather_timeout: int = 7):
        self.memory = memory
        self.weather_timeout = weather_timeout

    @staticmethod
    def _open_with_shell(target: str) -> bool:
        try:
            if os.name == "nt":
                os.startfile(target)  # type: ignore[attr-defined]
                return True
            subprocess.Popen([target])
            return True
        except Exception:
            return False

    def open_application(self, app_name: str) -> str:
        normalized = app_name.strip().lower()
        if not normalized:
            return "Mujhe app ka naam batao."

        known_aliases = {
            "chrome": "chrome",
            "google chrome": "chrome",
            "word": "winword",
            "excel": "excel",
            "vs code": "code",
            "vscode": "code",
            "photoshop": "photoshop",
        }
        candidate = known_aliases.get(normalized, normalized)
        path = self._discover_app_path(candidate)
        if path:
            subprocess.Popen([str(path)])
            self.memory.remember_app(app_name, str(path))
            return f"{app_name} open kar diya."

        if self._open_with_shell(candidate):
            self.memory.remember_app(app_name, None)
            return f"{app_name} launch karne ki koshish ki."
        return f"{app_name} system par nahi mila."

    @staticmethod
    def _discover_app_path(app_name: str) -> Optional[Path]:
        if os.name == "nt":
            try:
                import winreg

                safe_app_name = re.sub(r"[^a-zA-Z0-9._ -]", "", app_name).strip()
                if not safe_app_name:
                    return None
                registry_roots = [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]
                for root in registry_roots:
                    key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{safe_app_name}.exe"
                    try:
                        with winreg.OpenKey(root, key_path) as key:
                            value, _ = winreg.QueryValueEx(key, "")
                            app_path = Path(value)
                            if app_path.exists():
                                return app_path
                    except OSError:
                        continue
            except Exception:
                pass

        for base in os.environ.get("PATH", "").split(os.pathsep):
            candidate = Path(base) / app_name
            if candidate.exists():
                return candidate
            exe_candidate = Path(base) / f"{app_name}.exe"
            if exe_candidate.exists():
                return exe_candidate
        return None

    @staticmethod
    def open_website(url_or_name: str) -> str:
        target = url_or_name.strip()
        if not target:
            return "Website name missing hai."
        if not target.startswith(("http://", "https://")):
            if "." in target:
                target = f"https://{target}"
            else:
                target = f"https://www.{target}.com"
        webbrowser.open(target)
        return f"{target} open kiya."

    @staticmethod
    def google_search(query: str) -> str:
        if not query:
            return "Search query batao."
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Google par '{query}' search kar diya."

    @staticmethod
    def youtube_search(query: str) -> str:
        if not query:
            return "YouTube query missing hai."
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"YouTube par '{query}' search kar diya."

    def weather(self, city: str = "New Delhi") -> str:
        try:
            response = requests.get(f"https://wttr.in/{city}?format=3", timeout=self.weather_timeout)
            response.raise_for_status()
            return response.text.strip()
        except Exception:
            return "Weather service abhi reach nahi ho pa raha."

    @staticmethod
    def capture_screenshot(output_path: Path) -> str:
        try:
            from mss import mss
            from PIL import Image

            with mss() as sct:
                monitor = sct.monitors[1]
                grabbed = sct.grab(monitor)
                image = Image.frombytes("RGB", grabbed.size, grabbed.rgb)
                image.save(output_path)
            return f"Screenshot save ho gaya: {output_path}"
        except Exception as exc:
            return f"Screenshot fail hua: {exc}"
