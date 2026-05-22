from __future__ import annotations

import math
from typing import Callable

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

PULSE_AMPLITUDE = 0.1
LISTENING_SPEED = 2.4
DEFAULT_SPEED = 1.2


class OrbWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._phase = 0.0
        self._state = "Idle"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(40)

    def set_state(self, state: str) -> None:
        self._state = state
        self.update()

    def _tick(self) -> None:
        self._phase += 0.11
        self.update()

    def paintEvent(self, _event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(8, 16, 30))

        radius = min(self.width(), self.height()) * 0.23
        pulse = 1.0 + PULSE_AMPLITUDE * math.sin(
            self._phase * (LISTENING_SPEED if self._state == "Listening" else DEFAULT_SPEED)
        )
        color_map = {
            "Idle": QColor(71, 130, 255),
            "Listening": QColor(0, 255, 234),
            "Thinking": QColor(255, 179, 0),
            "Speaking": QColor(113, 255, 148),
        }
        core = color_map.get(self._state, QColor(71, 130, 255))
        center = self.rect().center()

        for i in range(3):
            layer_radius = radius * pulse * (1 + i * 0.25)
            alpha = max(40, 170 - i * 45)
            pen = QPen(QColor(core.red(), core.green(), core.blue(), alpha), 3)
            painter.setPen(pen)
            painter.drawEllipse(center, int(layer_radius), int(layer_radius))

        painter.setPen(QPen(QColor(240, 249, 255), 1))
        painter.drawText(self.rect(), Qt.AlignCenter, f"ARIA\n{self._state}")


class AriaMainWindow(QFrame):
    def __init__(self, send_command: Callable[[str], str]):
        super().__init__()
        self.send_command = send_command
        self.setWindowTitle("ARIA OS — Hybrid Human AI Assistant")
        self.resize(1024, 640)
        self.setObjectName("root")
        self._build_ui()
        self._apply_theme("dark")

    def _build_ui(self) -> None:
        root_layout = QHBoxLayout(self)

        left = QVBoxLayout()
        self.orb = OrbWidget()
        self.state_label = QLabel("State: Idle")
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setObjectName("stateLabel")
        left.addWidget(self.orb, stretch=8)
        left.addWidget(self.state_label, stretch=1)

        right = QVBoxLayout()
        self.log_list = QListWidget()
        self.log_list.setObjectName("logPanel")
        right.addWidget(self.log_list, stretch=8)

        quick = QHBoxLayout()
        for text in ["Open YouTube", "Weather", "Motivate Me", "Screenshot"]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda _, t=text: self._quick_command(t))
            quick.addWidget(btn)
        right.addLayout(quick, stretch=1)

        root_layout.addLayout(left, stretch=4)
        root_layout.addLayout(right, stretch=6)

    def _quick_command(self, label: str) -> None:
        mapping = {
            "Open YouTube": "Aria YouTube kholo",
            "Weather": "Aria weather batao",
            "Motivate Me": "Aria mujhe motivate karo",
            "Screenshot": "Aria screenshot lo",
        }
        command = mapping.get(label, label)
        self.append_log(f"USER: {command}")
        response = self.send_command(command)
        self.append_log(f"ASSISTANT: {response}")

    def append_log(self, text: str) -> None:
        self.log_list.addItem(QListWidgetItem(text))
        self.log_list.scrollToBottom()

    def set_state(self, state: str) -> None:
        self.orb.set_state(state)
        self.state_label.setText(f"State: {state}")

    def set_theme(self, theme: str) -> None:
        self._apply_theme(theme)

    def _apply_theme(self, theme: str) -> None:
        if theme == "light":
            self.setStyleSheet(
                """
                QFrame#root {background: #f4f8ff;}
                QLabel#stateLabel {color: #1f2c47; font-size: 16px; font-weight: 600;}
                QListWidget#logPanel {background: #ffffff; color: #12213a; border-radius: 12px; padding: 8px;}
                QPushButton {background: #d7e7ff; border-radius: 10px; padding: 10px; font-weight: 600;}
                QPushButton:hover {background: #c8dcff;}
                """
            )
            return
        self.setStyleSheet(
            """
            QFrame#root {background: #08101f;}
            QLabel#stateLabel {color: #8ed7ff; font-size: 16px; font-weight: 600;}
            QListWidget#logPanel {
                background: rgba(9, 25, 44, 0.82);
                color: #d9eeff;
                border: 1px solid #1c78a9;
                border-radius: 12px;
                padding: 8px;
            }
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0f3f72, stop:1 #1189bd);
                color: #f2fbff;
                border-radius: 10px;
                padding: 10px;
                font-weight: 600;
            }
            QPushButton:hover {background: #20a8e2;}
            """
        )


def ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
