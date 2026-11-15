from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List


class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type not in self._subs:
            self._subs[event_type] = []
        self._subs[event_type].append(callback)

    async def publish(self, event_type: str, data: Any = None) -> None:
        for cb in self._subs.get(event_type, []):
            try:
                res = cb(data)
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                # isolate subscriber errors
                pass
