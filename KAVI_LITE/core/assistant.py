from __future__ import annotations

import asyncio
import logging

from config.settings import REQUIRE_WAKE_WORD, WAKE_WORDS
from core.ai_engine import GroqAIEngine
from core.command_router import CommandRouter
from core.database import Database
from core.voice_engine import VoiceEngine


class Assistant:
    def __init__(self, on_state, on_subtitle) -> None:
        self.on_state = on_state
        self.on_subtitle = on_subtitle
        self.database = Database()
        self.ai_engine = GroqAIEngine(self.database)
        self.voice_engine = VoiceEngine()
        self.command_router = CommandRouter()
        self._stop_event = asyncio.Event()
        self._logger = logging.getLogger(__name__)

    def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        self.on_state("Idle")
        while not self._stop_event.is_set():
            self.on_state("Listening")
            try:
                text = await self.voice_engine.listen()
            except Exception:  # pragma: no cover - runtime optional
                self._logger.exception("Voice input failed")
                self.on_subtitle("Voice input is currently unavailable. Please check your microphone.")
                await asyncio.sleep(2)
                continue

            if not text:
                self.on_state("Idle")
                await asyncio.sleep(0.2)
                continue

            cleaned = self._strip_wake_words(text)
            if REQUIRE_WAKE_WORD and cleaned == text:
                self.on_state("Idle")
                continue

            self.on_subtitle(f"You: {cleaned}")
            response, handled = await self.command_router.route(cleaned)
            if not handled:
                self.on_state("Thinking")
                response = await self.ai_engine.generate_response(cleaned)

            if response:
                self.on_subtitle(f"KAVI: {response}")
                self.on_state("Speaking")
                await self.voice_engine.speak(response)
            self.on_state("Idle")
            await asyncio.sleep(0.1)

    def _strip_wake_words(self, text: str) -> str:
        cleaned = text.strip()
        lowered = cleaned.lower()
        for word in WAKE_WORDS:
            if lowered.startswith(word):
                return cleaned[len(word) :].strip(" ,")
        return cleaned
