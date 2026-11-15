from __future__ import annotations

from typing import Any, Dict

from shrp_ai.core.modules import BaseModule
from shrp_ai.context.manager import ContextManager, ExecutionContext
from shrp_ai.pipeline.pipeline import Pipeline
from shrp_ai.decision.base import DeterministicDecision


class SimulatedSensorModule(BaseModule):
    name = "simulated_sensor"
    version = "0.1.0"
    description = "Simulated sensor data demo module"

    def __init__(self):
        self.ctx_mgr = ContextManager()
        self.pipeline = Pipeline()
        self.decision = DeterministicDecision()
        # register stages
        async def validate(ctx: ExecutionContext):
            if "readings" not in ctx.data:
                raise ValueError("Missing readings")
            return {"valid": True}

        async def place_in_context(ctx: ExecutionContext):
            ctx.set("processed", True)
            return {"placed": True}

        self.pipeline.register("validate", validate)
        self.pipeline.register("place", place_in_context)

    async def execute(self, payload: Dict[str, Any]) -> Any:
        ctx = self.ctx_mgr.create(initial=payload)
        pipe_res = await self.pipeline.execute(ctx)
        decision = await self.decision.decide(ctx, payload, options=["log", "alert", "ignore"])
        return {
            "pipeline": pipe_res,
            "decision": {"selected": decision.selected, "reason": decision.reason, "confidence": decision.confidence},
        }
