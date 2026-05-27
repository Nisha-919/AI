from __future__ import annotations

import asyncio
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from config.settings import (
    LISTEN_SECONDS,
    PIPER_BINARY,
    PIPER_CONFIG_PATH,
    PIPER_MODEL_PATH,
    SAMPLE_RATE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_MODEL,
)

try:
    import numpy as np
    import sounddevice as sd
    import soundfile as sf
except ImportError:  # pragma: no cover - runtime optional
    np = None
    sd = None
    sf = None

try:
    from faster_whisper import WhisperModel
except ImportError:  # pragma: no cover - runtime optional
    WhisperModel = None


class VoiceEngine:
    def __init__(self) -> None:
        self.model = None

    def _ensure_model(self) -> None:
        if WhisperModel is None:
            raise RuntimeError("faster-whisper is not installed.")
        if self.model is None:
            self.model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type=WHISPER_COMPUTE_TYPE)

    def _record_audio(self) -> Any:
        if sd is None or np is None:
            raise RuntimeError("sounddevice/numpy not installed.")
        samples = int(LISTEN_SECONDS * SAMPLE_RATE)
        recording = sd.rec(samples, samplerate=SAMPLE_RATE, channels=1, dtype="float32")
        sd.wait()
        return recording.flatten()

    def _transcribe(self, audio: Any) -> str:
        self._ensure_model()
        segments, _info = self.model.transcribe(
            audio,
            language=None,
            vad_filter=True,
            beam_size=5,
        )
        text = " ".join(segment.text for segment in segments).strip()
        return text

    async def listen(self) -> str:
        return await asyncio.to_thread(self._listen_sync)

    def _listen_sync(self) -> str:
        audio = self._record_audio()
        return self._transcribe(audio)

    async def speak(self, text: str) -> None:
        if not text:
            return
        await asyncio.to_thread(self._speak_sync, text)

    def _speak_sync(self, text: str) -> None:
        model_path = Path(PIPER_MODEL_PATH)
        if not model_path.exists():
            return

        output_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                output_path = temp_file.name

            command = [PIPER_BINARY, "--model", str(model_path), "--output_file", output_path]
            config_path = Path(PIPER_CONFIG_PATH)
            if config_path.exists():
                command.extend(["--config", str(config_path)])

            subprocess.run(command, input=text.encode("utf-8"), check=True)

            if sd is None or sf is None:
                return
            audio, rate = sf.read(output_path, dtype="float32")
            sd.play(audio, rate)
            sd.wait()
        except (subprocess.SubprocessError, OSError):
            return
        finally:
            if output_path:
                try:
                    Path(output_path).unlink(missing_ok=True)
                except OSError:
                    pass
