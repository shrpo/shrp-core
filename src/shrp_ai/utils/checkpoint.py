from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional


class Checkpoint:
    @staticmethod
    def save_model_checkpoint(model, path: str | Path, optimizer=None, epoch: int = 0, config: Optional[Dict] = None) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # extract params
        layers = []
        if hasattr(model, 'layers'):
            for i, layer in enumerate(model.layers):
                layers.append({
                    "W": layer.W.tolist(),
                    "b": layer.b.tolist(),
                })
        payload = {
            "arch": {
                "input_dim": getattr(model, 'input_dim', None),
                "hidden_dims": getattr(model, 'hidden_dims', None),
                "output_dim": getattr(model, 'output_dim', None),
            },
            "layers": layers,
            "epoch": epoch,
            "config": config or {},
        }
        with p.open("w", encoding="utf-8") as f:
            json.dump(payload, f)

    save = save_model_checkpoint

    @staticmethod
    def load_model_checkpoint(model, path: str | Path, optimizer=None):
        p = Path(path)
        with p.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        layers_data = payload.get("layers", [])
        if hasattr(model, 'layers') and len(layers_data) == len(model.layers):
            import numpy as np
            for i, layer in enumerate(model.layers):
                layer.W = np.array(layers_data[i]["W"], dtype=np.float64)
                layer.b = np.array(layers_data[i]["b"], dtype=np.float64)
        return payload

    load = load_model_checkpoint

    @staticmethod
    def save(data: Dict, path: str | Path, extra: Optional[Dict] = None) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {"data": data, "extra": extra or {}}
        with p.open("w", encoding="utf-8") as f:
            json.dump(payload, f)

    @staticmethod
    def load(path: str | Path) -> Dict:
        with Path(path).open("r", encoding="utf-8") as f:
            return json.load(f)
