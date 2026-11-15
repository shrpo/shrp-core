from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional


@dataclass
class ExecutionContext:
    request_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def update(self, values: Dict[str, Any]) -> None:
        self.data.update(values)


class ContextManager:
    def __init__(self):
        self._contexts: Dict[str, ExecutionContext] = {}

    def create(self, request_id: Optional[str] = None, initial: Dict[str, Any] = None) -> ExecutionContext:
        rid = request_id or str(uuid.uuid4())
        ctx = ExecutionContext(request_id=rid, data=initial or {})
        self._contexts[rid] = ctx
        return ctx

    def get(self, request_id: str) -> Optional[ExecutionContext]:
        return self._contexts.get(request_id)

    def clear(self, request_id: str) -> None:
        self._contexts.pop(request_id, None)

    def clear_all(self) -> None:
        self._contexts.clear()
