from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AdapterContract:
    name: str
    version: str
    capabilities: Dict[str, Any]


class BaseAdapter:
    name: str = "base"
    version: str = "0.1.0"
    capabilities: Dict[str, Any] = {}

    async def initialize(self) -> None:
        pass

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    async def shutdown(self) -> None:
        pass


class AdapterRegistry:
    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}

    def register(self, adapter: BaseAdapter) -> None:
        if adapter.name in self._adapters:
            raise ValueError(f"Adapter '{adapter.name}' already registered")
        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> Optional[BaseAdapter]:
        return self._adapters.get(name)

    def list(self) -> Dict[str, Dict[str, Any]]:
        return {name: {"version": a.version, "capabilities": a.capabilities} for name, a in self._adapters.items()}
