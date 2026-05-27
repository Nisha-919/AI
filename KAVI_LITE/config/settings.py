from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
UI_DIR = BASE_DIR / "ui"
DATABASE_PATH = BASE_DIR / "database" / "kavi.db"
SCREENSHOT_DIR = ASSETS_DIR / "screenshots"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "8"))

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
LISTEN_SECONDS = float(os.getenv("LISTEN_SECONDS", "5"))
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
REQUIRE_WAKE_WORD = os.getenv("REQUIRE_WAKE_WORD", "false").lower() == "true"
WAKE_WORDS = ["kavi", "kavi lite", "hey kavi"]

PIPER_BINARY = os.getenv("PIPER_BINARY", "piper")
PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", str(ASSETS_DIR / "piper" / "model.onnx"))
PIPER_CONFIG_PATH = os.getenv("PIPER_CONFIG_PATH", str(ASSETS_DIR / "piper" / "model.onnx.json"))

APP_ALIASES = {
    "chrome": ["chrome", "google chrome"],
    "vscode": ["vscode", "vs code", "visual studio code", "code"],
}

APP_COMMANDS = {
    "chrome": os.getenv("CHROME_CMD", "chrome"),
    "vscode": os.getenv("VSCODE_CMD", "code"),
}

WEBSITE_ALIASES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
}
