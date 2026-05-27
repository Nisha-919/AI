# KAVI Lite

A lightweight futuristic desktop AI assistant with Hinglish voice interaction, a neon QML UI, and modular Python architecture. Designed to run on a normal laptop and easy to package into a Windows EXE.

## Features
- Voice input with faster-whisper (Hinglish-friendly recognition)
- GROQ API conversational AI with short-term memory
- Piper TTS voice replies
- App and website commands (Chrome, YouTube, VSCode, Google search, screenshots)
- Futuristic neon UI with animated orb and live subtitles
- Offline-friendly structure (local STT/TTS, API optional)

## Project Structure
```
KAVI_LITE/
├── main.py
├── core/
│   ├── assistant.py
│   ├── ai_engine.py
│   ├── voice_engine.py
│   ├── command_router.py
│   ├── automation.py
│   └── database.py
├── ui/
│   ├── main.qml
│   ├── orb.qml
│   └── subtitles.qml
├── assets/
├── database/
│   └── kavi.db
├── config/
│   └── settings.py
├── requirements.txt
├── build_exe.bat
└── README.md
```

## Setup
```bash
cd KAVI_LITE
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
Set these environment variables as needed:
- `GROQ_API_KEY`: required for AI chat
- `WHISPER_MODEL`: faster-whisper model name (default: `base`)
- `PIPER_MODEL_PATH` and `PIPER_CONFIG_PATH`: paths to Piper model files
- `CHROME_CMD`, `VSCODE_CMD`: override app launch commands

Place your Piper model files at:
```
assets/piper/model.onnx
assets/piper/model.onnx.json
```

## Run
```bash
python main.py
```

## EXE Build
```bash
pip install pyinstaller
build_exe.bat
```

## File Guide (explanations)
- `main.py`: Application entry point. Initializes the QML UI, connects async loop, and starts the assistant.
- `core/assistant.py`: Orchestrates the full flow (listen → intent → command/AI → reply).
- `core/ai_engine.py`: GROQ API client with conversation memory handling.
- `core/voice_engine.py`: Microphone capture + faster-whisper transcription + Piper TTS playback.
- `core/command_router.py`: Intent detection for apps, websites, search, and system commands.
- `core/automation.py`: Opens apps/websites and captures screenshots.
- `core/database.py`: SQLite storage for conversation history.
- `ui/main.qml`: Main UI layout and state bindings.
- `ui/orb.qml`: Animated glowing orb with state-driven effects.
- `ui/subtitles.qml`: Subtitle panel for live user/assistant text.
- `assets/`: Store optional icons, Piper models, and screenshots.
- `database/kavi.db`: Local SQLite database file (auto-created if missing).
- `config/settings.py`: Centralized configuration and command mappings.
- `requirements.txt`: Python dependencies for the assistant.
- `build_exe.bat`: One-file PyInstaller build script with assets/QML packaging.
- `README.md`: Project guide and usage instructions.
