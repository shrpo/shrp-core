from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ModelConfig:
    input_dim: int
    hidden_dims: list[int]
    output_dim: int
    activation: str = "relu"
    dropout: float = 0.0
    use_batchnorm: bool = False


@dataclass
class TrainConfig:
    batch_size: int = 32
    learning_rate: float = 1e-3
    epochs: int = 10
    weight_decay: float = 0.0
    checkpoint_dir: str = "checkpoints"
    device: str = "cpu"


@dataclass
class Config:
    model: ModelConfig
    train: TrainConfig

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Config":
        model = ModelConfig(**d["model"])
        train = TrainConfig(**d["train"])
        return cls(model=model, train=train)

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        with Path(path).open("r", encoding="utf-8") as f:
            d = json.load(f)
        return cls.from_dict(d)
