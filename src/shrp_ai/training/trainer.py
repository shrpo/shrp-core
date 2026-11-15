from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from shrp_ai.nn.loss import MSELoss
from shrp_ai.training.optim import SGD
from shrp_ai.memory.monitor import get_memory_stats


class Trainer:
    def __init__(self, model, optimizer: Optional[SGD] = None, criterion: Optional[MSELoss] = None, device: str = "cpu"):
        self.model = model
        self.optimizer = optimizer or SGD(lr=1e-3)
        self.criterion = criterion or MSELoss()
        self.device = device
        self.history: List[Dict] = []

    def train_step(self, x, y) -> float:
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        # forward
        if hasattr(self.model, 'forward'):
            out = self.model.forward(x)
        elif callable(self.model):
            out = self.model(x)
        else:
            raise ValueError("model has no forward method")
        # loss
        loss = self.criterion.forward(out, y)
        # backward
        grad = self.criterion.backward()
        if hasattr(self.model, 'backward'):
            self.model.backward(grad)
        else:
            raise ValueError("model has no backward method")
        # update
        self.optimizer.step(self.model)
        return float(loss)

    def evaluate_step(self, x, y) -> float:
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        if hasattr(self.model, 'forward'):
            out = self.model.forward(x)
        elif callable(self.model):
            out = self.model(x)
        else:
            raise ValueError("model has no forward method")
        loss = self.criterion.forward(out, y)
        return float(loss)

    def train_epoch(self, x, y, batch_size: int = 32, shuffle: bool = True):
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n = len(x)
        indices = np.arange(n)
        if shuffle:
            np.random.shuffle(indices)
        total_loss = 0.0
        num_batches = 0
        for i in range(0, n, batch_size):
            batch_idx = indices[i:i + batch_size]
            bx = x[batch_idx]
            by = y[batch_idx]
            loss = self.train_step(bx, by)
            total_loss += loss
            num_batches += 1
        avg_loss = total_loss / max(num_batches, 1)
        return avg_loss

    def evaluate(self, x, y):
        return self.evaluate_step(x, y)

    def fit(self, x_train, y_train, x_val=None, y_val=None, epochs: int = 10, batch_size: int = 32, shuffle: bool = True, early_stopping: bool = False, patience: int = 5):
        history = []
        best_val = float('inf')
        wait = 0
        for epoch in range(epochs):
            train_loss = self.train_epoch(x_train, y_train, batch_size=batch_size, shuffle=shuffle)
            val_loss = None
            if x_val is not None and y_val is not None:
                val_loss = self.evaluate(x_val, y_val)
            entry = {"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss}
            history.append(entry)
            self.history.append(entry)
            if early_stopping and val_loss is not None:
                if val_loss < best_val:
                    best_val = val_loss
                    wait = 0
                else:
                    wait += 1
                    if wait >= patience:
                        break
        return history
