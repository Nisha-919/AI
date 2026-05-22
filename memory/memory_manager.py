from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryManager:
    def __init__(self, db_path: Path, default_context_window: int = 12):
        self.db_path = db_path
        self.default_context_window = default_context_window
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    text TEXT NOT NULL,
                    language TEXT NOT NULL DEFAULT 'en',
                    emotion TEXT NOT NULL DEFAULT 'calm',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS recent_apps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    executable_path TEXT,
                    opened_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS security_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_message(self, role: str, text: str, language: str = "en", emotion: str = "calm") -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations(role, text, language, emotion, created_at) VALUES (?, ?, ?, ?, ?)",
                (role, text, language, emotion, self._now()),
            )

    def get_recent_conversation(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        effective_limit = limit or self.default_context_window
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, text, language, emotion, created_at FROM conversations ORDER BY id DESC LIMIT ?",
                (effective_limit,),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def set_preference(self, key: str, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO preferences(key, value, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (key, payload, self._now()),
            )

    def get_preference(self, key: str, default: Optional[Any] = None) -> Any:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM preferences WHERE key=?", (key,)).fetchone()
        if not row:
            return default
        try:
            return json.loads(row["value"])
        except json.JSONDecodeError:
            return default

    def remember_app(self, app_name: str, executable_path: Optional[str]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO recent_apps(app_name, executable_path, opened_at) VALUES (?, ?, ?)",
                (app_name, executable_path, self._now()),
            )

    def recent_apps(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT app_name, executable_path, opened_at
                FROM recent_apps ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def log_security_event(self, event: str, detail: str, severity: str = "warning") -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO security_logs(event, detail, severity, created_at) VALUES (?, ?, ?, ?)",
                (event, detail, severity, self._now()),
            )

    def security_failures_since(self, iso_datetime: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS total FROM security_logs
                WHERE severity IN ('warning', 'critical') AND created_at >= ?
                """,
                (iso_datetime,),
            ).fetchone()
        return int(row["total"]) if row else 0
