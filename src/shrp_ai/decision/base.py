from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Decision:
    selected: Any
    reason: str
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DecisionInterface:
    async def decide(self, context: Any, input_data: Dict[str, Any], options: List[Any], constraints: Dict[str, Any] = None) -> Decision:
        raise NotImplementedError


class DeterministicDecision(DecisionInterface):
    async def decide(self, context: Any, input_data: Dict[str, Any], options: List[Any], constraints: Dict[str, Any] = None) -> Decision:
        if not options:
            raise ValueError("No options provided")
        # Simple deterministic rule: pick first option
        return Decision(selected=options[0], reason="Deterministic baseline: selected first option", confidence=None, metadata={"baseline": True})
