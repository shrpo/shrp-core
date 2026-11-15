from __future__ import annotations

import asyncio
from typing import Any, Dict

from shrp_ai.core.engine import CoreEngine


class RuntimeManager:
    def __init__(self, core: CoreEngine = None, config: Dict[str, Any] = None):
        self.config = config or {}
        self.core = core or CoreEngine(self.config)

    async def start_library(self):
        if not self.core._initialized:
            await self.core.initialize()
        return self.core

    async def start_standalone(self, host: str = "127.0.0.1", port: int = 8000):
        if not self.core._initialized:
            await self.core.initialize()
        return {"host": host, "port": port, "core": self.core}
