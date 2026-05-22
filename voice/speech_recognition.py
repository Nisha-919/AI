from __future__ import annotations

import queue
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import soundfile as sf


class RealtimeSpeechRecognizer:
    def __init__(
        self,
        wake_words: list[str],
        on_text: Callable[[str], None],
        on_error: Optional[Callable[[str], None]] = None,
        sample_rate: int = 16000,
        chunk_seconds: float = 3.2,
        whisper_fp16: bool = False,
    ):
        self.wake_words = [word.lower() for word in wake_words]
        self.on_text = on_text
        self.on_error = on_error or (lambda msg: None)
        self.sample_rate = sample_rate
        self.chunk_seconds = chunk_seconds
        self.whisper_fp16 = whisper_fp16
        self._running = False
        self._listener_thread: Optional[threading.Thread] = None
        self._queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=20)
        self._wake_active = False
        self._load_models()

    def _load_models(self) -> None:
        self.whisper_model = None
        self.sounddevice = None
        try:
            import whisper
            import sounddevice as sd

            self.whisper_model = whisper.load_model("base")
            self.sounddevice = sd
        except Exception:
            self.whisper_model = None
            self.sounddevice = None

    def _record_loop(self) -> None:
        assert self.sounddevice is not None
        while self._running:
            try:
                frames = int(self.chunk_seconds * self.sample_rate)
                audio = self.sounddevice.rec(frames, samplerate=self.sample_rate, channels=1, dtype="float32")
                self.sounddevice.wait()
                self._queue.put(audio[:, 0].copy(), timeout=0.3)
            except queue.Full:
                self.on_error("Audio pipeline busy, dropping one voice chunk.")
                continue
            except Exception:
                time.sleep(0.4)

    def _transcribe(self, audio: np.ndarray) -> str:
        if self.whisper_model is None:
            return ""
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = Path(temp_wav.name)
        temp_wav.close()
        try:
            sf.write(temp_path, audio, self.sample_rate)
            result = self.whisper_model.transcribe(str(temp_path), language=None, fp16=self.whisper_fp16)
            return str(result.get("text", "")).strip()
        finally:
            temp_path.unlink(missing_ok=True)

    def _process_loop(self) -> None:
        while self._running:
            try:
                audio = self._queue.get(timeout=0.8)
            except queue.Empty:
                continue
            text = self._transcribe(audio)
            if not text:
                continue
            lowered = text.lower()
            if any(wake in lowered for wake in self.wake_words):
                self._wake_active = True
                self.on_text(text)
                continue
            if self._wake_active:
                self.on_text(text)
                self._wake_active = False

    def start(self) -> bool:
        if self._running or self.whisper_model is None or self.sounddevice is None:
            return False
        self._running = True
        self._listener_thread = threading.Thread(target=self._record_loop, name="STT-Record", daemon=True)
        self._listener_thread.start()
        threading.Thread(target=self._process_loop, name="STT-Process", daemon=True).start()
        return True

    def stop(self) -> None:
        self._running = False
