from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Callable, Dict, Optional


class TaskManager:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def submit(self, coro_func: Callable, *args, timeout: Optional[float] = None, **kwargs) -> str:
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {"status": "pending", "result": None, "error": None}

        async def _run():
            async with self._semaphore:
                self._tasks[task_id]["status"] = "running"
                try:
                    if timeout is not None:
                        result = await asyncio.wait_for(coro_func(*args, **kwargs), timeout=timeout)
                    else:
                        result = await coro_func(*args, **kwargs)
                    self._tasks[task_id]["status"] = "completed"
                    self._tasks[task_id]["result"] = result
                except asyncio.TimeoutError:
                    self._tasks[task_id]["status"] = "timeout"
                    self._tasks[task_id]["error"] = "timeout"
                except asyncio.CancelledError:
                    self._tasks[task_id]["status"] = "cancelled"
                    raise
                except Exception as e:
                    self._tasks[task_id]["status"] = "error"
                    self._tasks[task_id]["error"] = str(e)

        task = asyncio.create_task(_run())
        self._tasks[task_id]["task"] = task
        return task_id

    def status(self, task_id: str) -> Dict[str, Any]:
        if task_id not in self._tasks:
            raise ValueError(f"Task '{task_id}' not found")
        info = dict(self._tasks[task_id])
        info.pop("task", None)
        return info

    def cancel(self, task_id: str) -> None:
        if task_id not in self._tasks:
            raise ValueError(f"Task '{task_id}' not found")
        task = self._tasks[task_id].get("task")
        if task and not task.done():
            task.cancel()

    async def shutdown(self) -> None:
        for tid, info in self._tasks.items():
            task = info.get("task")
            if task and not task.done():
                task.cancel()
        await asyncio.sleep(0)
