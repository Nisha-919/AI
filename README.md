# ARIA OS — Hybrid Human AI Assistant

Production-grade voice-first desktop AI assistant architecture with modular Python design.

## Architecture

```
config/       # Centralized runtime config and constants
core/         # Assistant engine and orchestration logic
voice/        # Real-time STT, TTS, and voice authentication
automation/   # App/system/browser/screen operations
gui/          # PyQt5 futuristic control UI
memory/       # Long-term memory + security logs (SQLite)
utils/        # Logging and shared utilities
```

## Features Implemented

- Wake-word driven continuous voice loop (`Hey Aria`, `Aria`)
- Multilingual detection (English/Hindi/Hinglish)
- Intent scoring + flexible command parsing
- Dynamic app launch with discovery fallback and memory
- Browser, Google, YouTube, screenshot and weather actions
- OCR + PDF text extraction + screen summarization
- Voice mode switching (male/female) and asynchronous TTS
- Voice security module (passphrase + MFCC speaker verification)
- Memory system for conversations, preferences, recent apps, security logs
- Futuristic PyQt5 GUI (animated orb, state indicators, command log, themes)
- Resilient state handling and non-blocking worker threads

## Installation

1. Create a virtual environment:
   - `python -m venv .venv`
   - Windows: `.venv\\Scripts\\activate`
   - Linux/macOS: `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Optional external tools:
   - Tesseract OCR engine for OCR features
   - FFmpeg/audio codecs for richer TTS playback environments

## Run

```bash
python main.py
```

If microphone/audio model dependencies are unavailable, GUI still runs and quick-command buttons/manual processing remain functional.

## Testing Guide

- Unit tests: `pytest -q`
- Style check: `flake8 .`
- Format check: `black --check .`
- Syntax smoke test: `python -m compileall .`

## EXE Build (PyInstaller)

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --name "ARIA-OS" --icon=assets/aria.ico main.py
```

Recommended packaging additions:
- Add splash screen via `--splash assets/splash.png`
- Include models/data with `--add-data`
- Create installer with Inno Setup / NSIS

## Scalability Recommendations

- Replace local intent model with pluggable LLM policy router
- Add event bus (Redis/NATS) for skill microservices
- Persist embeddings for semantic memory retrieval
- Introduce plugin SDK for third-party command packs
- Add cross-device profile sync and encrypted memory storage
