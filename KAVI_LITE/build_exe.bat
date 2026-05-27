@echo off
setlocal

set NAME=KAVI_Lite
set ROOT=%~dp0
set MAIN=%ROOT%main.py
set ICON=%ROOT%assets\icon.ico

set ICON_FLAG=
if exist "%ICON%" set ICON_FLAG=--icon="%ICON%"

pyinstaller --noconfirm --clean --onefile --windowed --name "%NAME%" %ICON_FLAG% ^
  --add-data "%ROOT%ui;ui" ^
  --add-data "%ROOT%assets;assets" ^
  --collect-all PySide6 ^
  --collect-all faster_whisper ^
  --hidden-import piper ^
  --hidden-import piper_phonemize ^
  "%MAIN%"

echo Build complete. Check the dist folder.
pause
endlocal
