from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


PROJECT_NAME = "ARIA OS — Hybrid Human AI Assistant"
APP_VERSION = "2.0.0"
DEFAULT_DB_NAME = "aria_memory.db"
DEFAULT_LOG_FILE = "aria.log"


@dataclass(slots=True)
class VoiceProfile:
    name: str
    tts_voice: str
    rate: int
    volume: float
    style: str


@dataclass(slots=True)
class AriaConfig:
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])
    data_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    db_path: Path = field(init=False)
    wake_words: List[str] = field(default_factory=lambda: ["hey aria", "aria"])
    auth_passphrase: str = "nisha access"
    auth_threshold: float = 0.82
    language_priority: List[str] = field(default_factory=lambda: ["en", "hi", "hinglish"])
    voice_profiles: Dict[str, VoiceProfile] = field(
        default_factory=lambda: {
            "professional": VoiceProfile("professional", "en-US-GuyNeural", 175, 0.95, "serious"),
            "friendly": VoiceProfile("friendly", "en-US-JennyNeural", 170, 0.96, "chat"),
            "futuristic": VoiceProfile("futuristic", "en-US-AriaNeural", 168, 0.94, "newscast"),
            "calm": VoiceProfile("calm", "en-IN-NeerjaNeural", 160, 0.9, "customerservice"),
            "robotic": VoiceProfile("robotic", "en-GB-RyanNeural", 158, 0.9, "narration-professional"),
        }
    )
    male_voice: str = "en-US-GuyNeural"
    female_voice: str = "en-IN-NeerjaNeural"
    default_theme: str = "dark"
    default_city: str = "New Delhi"
    default_tts_voice: str = "en-IN-NeerjaNeural"
    min_intent_confidence: float = 0.18
    security_window_minutes: int = 15
    memory_context_window: int = 12
    weather_api_timeout: int = 7
    whisper_fp16: bool = False
    max_security_failures: int = 3
    continuous_mode: bool = True

    def __post_init__(self) -> None:
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        self.db_path = self.data_dir / DEFAULT_DB_NAME
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
