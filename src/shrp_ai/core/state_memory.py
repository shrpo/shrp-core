from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


class StateManager:
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._snapshots: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    def delete(self, key: str) -> None:
        self._state.pop(key, None)

    def clear(self) -> None:
        self._state.clear()

    def snapshot(self, name: Optional[str] = None) -> str:
        name = name or str(uuid.uuid4())
        self._snapshots[name] = json.loads(json.dumps(self._state))
        return name

    def restore(self, name: str) -> None:
        if name not in self._snapshots:
            raise ValueError(f"Snapshot '{name}' not found")
        self._state = json.loads(json.dumps(self._snapshots[name]))


class MemoryManager:
    def __init__(self, db_path: str | Path = None):
        import sqlite3
        if db_path is None:
            db_path = Path.cwd() / "shrp_core.db"
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS records (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at REAL,
                updated_at REAL
            )"""
        )
        conn.commit()
        conn.close()

    def save(self, key: str, value: Any) -> None:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        now = time.time()
        cur.execute(
            "INSERT OR REPLACE INTO records (key, value, created_at, updated_at) VALUES (?, ?, COALESCE((SELECT created_at FROM records WHERE key=?), ?), ?)",
            (key, json.dumps(value), key, now, now),
        )
        conn.commit()
        conn.close()

    def get(self, key: str) -> Optional[Any]:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT value FROM records WHERE key=?", (key,))
        row = cur.fetchone()
        conn.close()
        if row is None:
            return None
        return json.loads(row[0])

    def delete(self, key: str) -> None:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM records WHERE key=?", (key,))
        conn.commit()
        conn.close()

    def list(self) -> Dict[str, Any]:
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM records")
        rows = cur.fetchall()
        conn.close()
        result = {}
        for k, v in rows:
            result[k] = json.loads(v)
        return result
