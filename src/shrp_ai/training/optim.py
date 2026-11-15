from __future__ import annotations

from typing import Dict, Optional

import numpy as np


class SGD:
    def __init__(self, lr: float = 1e-3, momentum: float = 0.0):
        if lr <= 0:
            raise ValueError("learning rate must be positive")
        self.lr = lr
        self.momentum = momentum
        self.velocities = {}

    def step(self, model):
        if hasattr(model, 'step'):
            model.step(self.lr)
            return
        # try to step layers
        if hasattr(model, 'layers'):
            for layer in model.layers:
                if hasattr(layer, 'step'):
                    layer.step(self.lr)
            return
        raise ValueError("model has no step method")
