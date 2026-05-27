from __future__ import annotations

import asyncio
from typing import Tuple

from config.settings import APP_ALIASES, WEBSITE_ALIASES
from core import automation


class CommandRouter:
    async def route(self, text: str) -> Tuple[str, bool]:
        normalized = text.lower().strip()

        if self._matches(normalized, ["screenshot", "screen shot", "screenshot lo", "screenshot le"]):
            path = await asyncio.to_thread(automation.take_screenshot)
            if path:
                return f"Screenshot saved at {path}", True
            return "Screenshot feature is unavailable.", True

        app_key = self._match_app(normalized)
        if app_key:
            launched = await asyncio.to_thread(automation.open_app, app_key)
            if launched:
                return f"Opening {app_key}.", True
            return f"Could not open {app_key}.", True

        website = self._match_website(normalized)
        if website:
            opened = await asyncio.to_thread(automation.open_website, website)
            if opened:
                return "Opening website.", True
            return "Unable to open website.", True

        if "search" in normalized or "dhoondo" in normalized or "dhoond" in normalized:
            query = self._extract_query(normalized)
            if not query:
                return "Tell me what to search for.", True
            opened = await asyncio.to_thread(automation.google_search, query)
            if opened:
                return f"Searching for {query}.", True
            return "Unable to start search.", True

        return "", False

    @staticmethod
    def _matches(text: str, phrases: list[str]) -> bool:
        return any(phrase in text for phrase in phrases)

    @staticmethod
    def _match_app(text: str) -> str | None:
        for app_key, aliases in APP_ALIASES.items():
            if any(alias in text for alias in aliases) and ("open" in text or "kholo" in text):
                return app_key
        return None

    @staticmethod
    def _match_website(text: str) -> str | None:
        for key, url in WEBSITE_ALIASES.items():
            if key in text and ("open" in text or "kholo" in text):
                return url
        return None

    @staticmethod
    def _extract_query(text: str) -> str:
        cleanup = text
        for token in ["google", "search", "karo", "kar do", "please", "dhoondo", "dhoond"]:
            cleanup = cleanup.replace(token, "")
        return " ".join(cleanup.split()).strip()
