from __future__ import annotations

import asyncio
from typing import Any, Dict

from shrp_ai.core.modules import ModuleManager, EchoModule
from shrp_ai.core.interfaces import Request, Response
from shrp_ai.core.state_memory import StateManager, MemoryManager
from shrp_ai.core.events import EventBus
from shrp_ai.core.tasks import TaskManager


class CoreEngine:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.modules = ModuleManager()
        self.state = StateManager()
        self.memory = MemoryManager(self.config.get("db_path"))
        self.events = EventBus()
        self.tasks = TaskManager(max_concurrent=self.config.get("max_concurrent_tasks", 10))
        self._initialized = False

    async def initialize(self) -> None:
        # register default modules
        if "echo" not in [m["name"] for m in self.modules.list_modules()]:
            try:
                self.modules.register(EchoModule())
            except Exception:
                pass
        await self.modules.initialize_all()
        self._initialized = True

    async def shutdown(self) -> None:
        await self.modules.shutdown_all()
        await self.tasks.shutdown()
        if hasattr(self.memory, "close"):
            self.memory.close()
        self._initialized = False

    async def handle_request(self, req: Request) -> Response:
        try:
            result = await self.modules.execute(req.module, req.payload)
            return Response(request_id=req.request_id, status="ok", result=result)
        except Exception as e:
            return Response(request_id=req.request_id, status="error", error=str(e))

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "initialized": self._initialized}

    def status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "modules": len(self.modules.list_modules()),
            "config": self.config,
        }