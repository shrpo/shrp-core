from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ModuleContract:
    name: str
    version: str = "0.1.0"
    description: str = ""


class BaseModule:
    name: str = "base"
    version: str = "0.1.0"
    description: str = ""

    async def initialize(self) -> None:
        pass

    async def execute(self, payload: Dict[str, Any]) -> Any:
        raise NotImplementedError

    async def shutdown(self) -> None:
        pass


class EchoModule(BaseModule):
    name = "echo"
    version = "0.1.0"
    description = "Echo module for testing"

    async def execute(self, payload: Dict[str, Any]) -> Any:
        return {"echo": payload}


class ModuleManager:
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}
        self._enabled: Dict[str, bool] = {}

    def register(self, module: BaseModule) -> None:
        if module.name in self._modules:
            raise ValueError(f"Module '{module.name}' already registered")
        self._modules[module.name] = module
        self._enabled[module.name] = True

    def get(self, name: str) -> Optional[BaseModule]:
        return self._modules.get(name)

    def list_modules(self) -> List[Dict[str, Any]]:
        result = []
        for name, mod in self._modules.items():
            result.append({
                "name": name,
                "version": getattr(mod, "version", "0.1.0"),
                "description": getattr(mod, "description", ""),
                "enabled": self._enabled.get(name, True),
            })
        return result

    def enable(self, name: str) -> None:
        if name not in self._modules:
            raise ValueError(f"Module '{name}' not found")
        self._enabled[name] = True

    def disable(self, name: str) -> None:
        if name not in self._modules:
            raise ValueError(f"Module '{name}' not found")
        self._enabled[name] = False

    async def execute(self, name: str, payload: Dict[str, Any]) -> Any:
        if name not in self._modules:
            raise ValueError(f"Module '{name}' not found")
        if not self._enabled.get(name, True):
            raise ValueError(f"Module '{name}' is disabled")
        mod = self._modules[name]
        return await mod.execute(payload)

    async def initialize_all(self) -> None:
        for mod in self._modules.values():
            await mod.initialize()

    async def shutdown_all(self) -> None:
        for mod in self._modules.values():
            await mod.shutdown()
