from __future__ import annotations

import signal
import sys
from functools import partial

from config.constants import APP_VERSION, AriaConfig, PROJECT_NAME
from core.assistant_engine import AssistantEngine
from gui.main_window import AriaMainWindow, ensure_app
from utils.logger import get_logger


def main() -> int:
    config = AriaConfig()
    logger = get_logger("aria", config.logs_dir / "aria.log")
    logger.info("Starting %s v%s", PROJECT_NAME, APP_VERSION)

    app = ensure_app()

    def noop_send(_: str) -> str:
        return "Engine is starting..."

    window = AriaMainWindow(send_command=noop_send)
    engine = AssistantEngine(config=config, logger=logger)

    def on_engine_event(event: str, payload: str) -> None:
        if event == "state":
            window.set_state(payload)
        elif event == "log":
            window.append_log(payload)
        elif event == "theme":
            window.set_theme(payload)

    engine.on_event = on_engine_event
    window.send_command = partial(engine.process_text_command)
    window.show()

    engine.start()

    def _shutdown(*_args):
        logger.info("Shutting down ARIA.")
        engine.shutdown()
        app.quit()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    exit_code = app.exec_()
    engine.shutdown()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
