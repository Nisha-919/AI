from __future__ import annotations

import asyncio
import queue
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pyttsx3


@dataclass(slots=True)
class SpeechRequest:
    text: str
    language: str
    emotion: str
    voice: str


class TextToSpeechEngine:
    def __init__(self, default_voice: str = "en-IN-NeerjaNeural"):
        self._queue: queue.Queue[SpeechRequest] = queue.Queue()
        self._running = True
        self._pyttsx3 = pyttsx3.init()
        self._profile_voice = default_voice
        self._pygame_ready = False
        self._init_pygame()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True, name="TTS-Worker")
        self._worker.start()

    def set_voice(self, voice_name: str) -> None:
        self._profile_voice = voice_name

    def speak(self, text: str, language: str = "en", emotion: str = "calm", voice: str = "") -> None:
        self._queue.put(SpeechRequest(text=text, language=language, emotion=emotion, voice=voice or self._profile_voice))

    def stop(self) -> None:
        self._running = False
        self._queue.put(SpeechRequest(text="", language="en", emotion="calm", voice=""))

    def _worker_loop(self) -> None:
        while self._running:
            request = self._queue.get()
            if not request.text:
                continue
            if not self._speak_edge_tts(request):
                self._speak_pyttsx3(request)

    def _init_pygame(self) -> None:
        try:
            import pygame

            pygame.mixer.init()
            self._pygame_ready = True
        except Exception:
            self._pygame_ready = False

    def _speak_edge_tts(self, request: SpeechRequest) -> bool:
        if not self._pygame_ready:
            return False
        audio_path: Optional[Path] = None
        try:
            import edge_tts
            import pygame

            async def _generate() -> Path:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_path = Path(temp_file.name)
                temp_file.close()
                try:
                    communicate = edge_tts.Communicate(
                        text=request.text, voice=request.voice or self._profile_voice
                    )
                    await communicate.save(str(temp_path))
                except Exception:
                    temp_path.unlink(missing_ok=True)
                    raise
                return temp_path

            audio_path = asyncio.run(_generate())
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(20)
            return True
        except Exception:
            return False
        finally:
            if audio_path is not None:
                audio_path.unlink(missing_ok=True)

    def _speak_pyttsx3(self, request: SpeechRequest) -> None:
        rate = 168
        if request.emotion == "serious":
            rate = 155
        elif request.emotion == "happy":
            rate = 182
        self._pyttsx3.setProperty("rate", rate)
        self._pyttsx3.setProperty("volume", 0.96)
        self._pyttsx3.say(request.text)
        self._pyttsx3.runAndWait()
