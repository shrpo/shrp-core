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
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cur = self._conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS records (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at REAL,
                updated_at REAL
            )"""
        )
        self._conn.commit()

    def save(self, key: str, value: Any) -> None:
        cur = self._conn.cursor()
        now = time.time()
        cur.execute(
            "INSERT OR REPLACE INTO records (key, value, created_at, updated_at) VALUES (?, ?, COALESCE((SELECT created_at FROM records WHERE key=?), ?), ?)",
            (key, json.dumps(value), key, now, now),
        )
        self._conn.commit()

    def get(self, key: str) -> Optional[Any]:
        cur = self._conn.cursor()
        cur.execute("SELECT value FROM records WHERE key=?", (key,))
        row = cur.fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def delete(self, key: str) -> None:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM records WHERE key=?", (key,))
        self._conn.commit()

    def list(self) -> Dict[str, Any]:
        cur = self._conn.cursor()
        cur.execute("SELECT key, value FROM records")
        rows = cur.fetchall()
        result = {}
        for row in rows:
            result[row["key"]] = json.loads(row["value"])
        return result

    def close(self) -> None:
        self._conn.close()
