from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Request:
    request_id: str
    module: str
    payload: Dict[str, Any]


@dataclass
class Response:
    request_id: str
    status: str  # ok|error
    result: Optional[Any] = None
    error: Optional[str] = None
