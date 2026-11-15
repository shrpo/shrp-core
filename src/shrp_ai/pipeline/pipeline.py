from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional

from shrp_ai.context.manager import ExecutionContext


StageFunc = Callable[[ExecutionContext], Awaitable[Any]]


@dataclass
class StageResult:
    name: str
    success: bool
    result: Any = None
    error: Optional[str] = None


class Pipeline:
    def __init__(self, stages: List[tuple[str, StageFunc]] = None, timeout: Optional[float] = None):
        self.stages = stages or []
        self.timeout = timeout

    def register(self, name: str, func: StageFunc) -> None:
        self.stages.append((name, func))

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        results = []
        for name, func in self.stages:
            try:
                if self.timeout is not None:
                    res = await asyncio.wait_for(func(ctx), timeout=self.timeout)
                else:
                    res = await func(ctx)
                results.append(StageResult(name=name, success=True, result=res).__dict__)
                ctx.metadata[f"stage_{name}"] = res
            except Exception as e:
                results.append(StageResult(name=name, success=False, error=str(e)).__dict__)
                raise
        return {"context_id": ctx.request_id, "stages": results, "context_data": ctx.data}
