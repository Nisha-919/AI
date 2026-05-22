from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

from automation.screen_understanding import ScreenUnderstanding
from automation.system_controller import SystemController
from commands import CommandBrain
from config.constants import AriaConfig
from memory.memory_manager import MemoryManager
from voice.speech_recognition import RealtimeSpeechRecognizer
from voice.text_to_speech import TextToSpeechEngine
from voice.voice_authentication import VoiceAuthenticator


class AssistantEngine:
    def __init__(self, config: AriaConfig, logger, on_event: Optional[Callable[[str, str], None]] = None):
        self.config = config
        self.logger = logger
        self.on_event = on_event or (lambda event, payload: None)
        self.memory = MemoryManager(config.db_path, default_context_window=config.memory_context_window)
        self.command_brain = CommandBrain(min_confidence=config.min_intent_confidence)
        self.system = SystemController(self.memory, weather_timeout=config.weather_api_timeout)
        self.screen = ScreenUnderstanding()
        self.tts = TextToSpeechEngine(default_voice=config.default_tts_voice)
        self.voice_auth = VoiceAuthenticator(threshold=config.auth_threshold)
        self.state = "Idle"
        self.is_locked = False
        self.failed_attempts = 0
        self.current_voice = config.voice_profiles["friendly"].tts_voice
        self.tts.set_voice(self.current_voice)
        self.recognizer = RealtimeSpeechRecognizer(
            config.wake_words, self._handle_raw_speech, whisper_fp16=config.whisper_fp16
        )

    def start(self) -> None:
        self._set_state("Listening")
        started = self.recognizer.start()
        if not started:
            self._set_state("Idle")
            self.logger.warning("Speech recognizer unavailable. Falling back to manual command mode.")
            self.publish("system", "Voice pipeline unavailable. Use process_text_command() for testing.")
        else:
            self.speak("ARIA online. Main sun rahi hoon.")

    def shutdown(self) -> None:
        self._set_state("Idle")
        self.recognizer.stop()
        self.tts.stop()

    def process_text_command(self, text: str) -> str:
        return self._process(text)

    def _handle_raw_speech(self, text: str) -> None:
        threading.Thread(target=self._process, args=(text,), daemon=True, name="Command-Worker").start()

    def _set_state(self, state: str) -> None:
        self.state = state
        self.on_event("state", state)

    def publish(self, role: str, text: str) -> None:
        lang = self.command_brain.detect_language(text)
        emotion = "calm"
        self.memory.add_message(role=role, text=text, language=lang, emotion=emotion)
        self.on_event("log", f"{role.upper()}: {text}")

    def speak(self, text: str, language: str = "en", emotion: str = "calm") -> None:
        self._set_state("Speaking")
        self.tts.speak(text=text, language=language, emotion=emotion, voice=self.current_voice)
        self.publish("assistant", text)
        self._set_state("Listening")

    def _process(self, text: str) -> str:
        incoming = text.strip()
        if not incoming:
            return ""
        self._set_state("Thinking")
        self.publish("user", incoming)
        if self.security_should_lock():
            self.is_locked = True
        if self.is_locked:
            response = "Security lock active hai. Authorized passphrase aur voice verification required."
            self.speak(response, emotion="serious")
            return response

        intent = self.command_brain.classify(incoming)
        self.logger.info("Intent=%s confidence=%.2f entities=%s", intent.intent, intent.confidence, intent.entities)
        response = self._dispatch(intent.intent, intent.entities, incoming)
        self.speak(response, language=self.command_brain.detect_language(incoming))
        return response

    def _dispatch(self, intent: str, entities: dict[str, str], text: str) -> str:
        if intent == "open_app":
            return self.system.open_application(entities.get("app_name", text))
        if intent == "open_website":
            return self.system.open_website(entities.get("url_or_name", ""))
        if intent == "youtube_search":
            return self.system.youtube_search(entities.get("query", ""))
        if intent == "google_search":
            return self.system.google_search(entities.get("query", ""))
        if intent == "play_music":
            return "Spotify control module ready hai. 'Spotify play <song>' bolo."
        if intent == "screenshot":
            output = self.config.data_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            return self.system.capture_screenshot(output)
        if intent == "screen_summary":
            output = self.config.data_dir / "latest_screen.png"
            self.system.capture_screenshot(output)
            extracted = self.screen.extract_text_from_image(output)
            return self.screen.summarize_text(extracted)
        if intent == "set_voice_male":
            self.current_voice = self.config.male_voice
            self.tts.set_voice(self.current_voice)
            self.memory.set_preference("voice_mode", "male")
            return "Male voice mode enabled."
        if intent == "set_voice_female":
            self.current_voice = self.config.female_voice
            self.tts.set_voice(self.current_voice)
            self.memory.set_preference("voice_mode", "female")
            return "Female voice mode enabled."
        if intent == "set_theme_dark":
            self.memory.set_preference("theme", "dark")
            self.on_event("theme", "dark")
            return "Dark theme apply kar diya."
        if intent == "set_theme_light":
            self.memory.set_preference("theme", "light")
            self.on_event("theme", "light")
            return "Light theme apply kar diya."
        if intent == "help":
            return (
                "Main app launch, website open, YouTube/Google search, screenshot, screen summarize, "
                "voice switch, theme switch aur memory preferences handle kar sakti hoon."
            )
        if intent == "exit":
            self.shutdown()
            return "Goodbye. ARIA standby mode me chali gayi."

        if "weather" in text.lower() or "mausam" in text.lower():
            return self.system.weather(self.config.default_city)
        if "motivate" in text.lower():
            return "Tum strong ho. Chhote steps bhi progress hote hain. Aaj ka ek win choose karo, main saath hoon."
        if "pdf" in text.lower():
            maybe_pdf = self._find_latest_pdf()
            if maybe_pdf:
                return self.screen.summarize_pdf(maybe_pdf)
            return "Recent PDF nahi mila."
        return "Samajh gayi, lekin is request ke liye mujhe thoda aur context chahiye."

    def _find_latest_pdf(self) -> Optional[Path]:
        pdfs = sorted(self.config.base_dir.rglob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        return pdfs[0] if pdfs else None

    def security_should_lock(self) -> bool:
        horizon = (
            datetime.now(timezone.utc) - timedelta(minutes=self.config.security_window_minutes)
        ).isoformat()
        return self.memory.security_failures_since(horizon) >= self.config.max_security_failures
