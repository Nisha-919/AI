from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from qasync import QEventLoop

from core.assistant import Assistant


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


class AssistantController(QObject):
    stateChanged = Signal()
    subtitleChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._state = "Idle"
        self._subtitle = "Say 'KAVI' to begin."
        self.assistant = Assistant(self._update_state, self._update_subtitle)

    def _update_state(self, state: str) -> None:
        if state != self._state:
            self._state = state
            self.stateChanged.emit()

    def _update_subtitle(self, text: str) -> None:
        if text != self._subtitle:
            self._subtitle = text
            self.subtitleChanged.emit()

    def get_state(self) -> str:
        return self._state

    def get_subtitle(self) -> str:
        return self._subtitle

    state = Property(str, get_state, notify=stateChanged)
    subtitle = Property(str, get_subtitle, notify=subtitleChanged)

    async def start(self) -> None:
        await self.assistant.run()

    def stop(self) -> None:
        self.assistant.stop()


def main() -> int:
    app = QGuiApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    icon_path = resource_path("assets/icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    controller = AssistantController()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", controller)
    qml_path = resource_path("ui/main.qml")
    engine.load(str(qml_path))
    if not engine.rootObjects():
        return 1

    app.aboutToQuit.connect(controller.stop)
    loop.create_task(controller.start())

    with loop:
        loop.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
