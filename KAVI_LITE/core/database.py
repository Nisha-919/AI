from pathlib import Path
import sqlite3
import threading

from config.settings import DATABASE_PATH, MAX_HISTORY


class Database:
    def __init__(self, path: Path = DATABASE_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self._lock = threading.Lock()
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self.connection.commit()

    def add_message(self, role: str, content: str) -> None:
        with self._lock:
            self.connection.execute(
                "INSERT INTO messages (role, content) VALUES (?, ?)",
                (role, content),
            )
            self.connection.commit()

    def fetch_recent(self, limit: int = MAX_HISTORY) -> list[dict[str, str]]:
        with self._lock:
            cursor = self.connection.execute(
                "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
        return [{"role": role, "content": content} for role, content in reversed(rows)]

    def close(self) -> None:
        with self._lock:
            self.connection.close()
