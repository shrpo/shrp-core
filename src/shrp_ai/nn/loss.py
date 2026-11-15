from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np


class MSELoss:
    def __init__(self):
        self.pred = None
        self.target = None

    def forward(self, pred, target):
        pred = np.asarray(pred, dtype=np.float64)
        target = np.asarray(target, dtype=np.float64)
        if pred.shape != target.shape:
            # try to broadcast if compatible
            pass
        self.pred = pred
        self.target = target
        diff = pred - target
        loss = np.mean(diff ** 2)
        return loss

    def backward(self):
        if self.pred is None or self.target is None:
            raise ValueError("forward must be called before backward")
        diff = self.pred - self.target
        n = diff.size
        grad = 2.0 * diff / n
        return grad

    def __call__(self, pred, target):
        return self.forward(pred, target)
