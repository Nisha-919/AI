from pathlib import Path
import sqlite3

from config.settings import DATABASE_PATH, MAX_HISTORY


class Database:
    def __init__(self, path: Path = DATABASE_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self._init_schema()

    def _init_schema(self) -> None:
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
        self.connection.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content),
        )
        self.connection.commit()

    def fetch_recent(self, limit: int = MAX_HISTORY) -> list[dict[str, str]]:
        cursor = self.connection.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [{"role": role, "content": content} for role, content in reversed(rows)]

    def close(self) -> None:
        self.connection.close()
