from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np


class SimpleLinear:
    def __init__(self, input_dim: int, output_dim: int):
        self.input_dim = input_dim
        self.output_dim = output_dim
        # Xavier/Glorot initialization
        limit = np.sqrt(6.0 / (input_dim + output_dim))
        self.W = np.random.uniform(-limit, limit, (input_dim, output_dim)).astype(np.float64)
        self.b = np.zeros((1, output_dim), dtype=np.float64)
        # Cache for backward
        self._x = None
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)

    def forward(self, x):
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        self._x = x
        out = x @ self.W + self.b
        return out

    def backward(self, dout):
        dout = np.asarray(dout, dtype=np.float64)
        if dout.ndim == 1:
            dout = dout.reshape(1, -1)
        if self._x is None:
            raise ValueError("forward must be called before backward")
        # dW = X^T @ dout, db = sum(dout), dX = dout @ W^T
        self.dW = self._x.T @ dout
        self.db = np.sum(dout, axis=0, keepdims=True)
        dx = dout @ self.W.T
        return dx

    def step(self, lr: float):
        if self.dW is None or self.db is None:
            raise ValueError("backward must be called before step")
        self.W = self.W - lr * self.dW
        self.b = self.b - lr * self.db


class SHRPNet:
    def __init__(self, input_dim: int, hidden_dims: List[int] = None, output_dim: int = 1, activation: str = "linear", **kwargs):
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims or []
        self.output_dim = output_dim
        self.activation = activation
        dims = [input_dim] + list(self.hidden_dims) + [output_dim]
        self.layers: List[SimpleLinear] = []
        for i in range(len(dims) - 1):
            self.layers.append(SimpleLinear(dims[i], dims[i + 1]))

    def forward(self, x):
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        for layer in self.layers:
            x = layer.forward(x)
        return x

    def backward(self, dout):
        dout = np.asarray(dout, dtype=np.float64)
        if dout.ndim == 1:
            dout = dout.reshape(1, -1)
        for layer in reversed(self.layers):
            dout = layer.backward(dout)
        return dout

    def step(self, lr: float):
        for layer in self.layers:
            layer.step(lr)

    def get_params(self):
        params = []
        for i, layer in enumerate(self.layers):
            params.append({
                "W": layer.W.copy(),
                "b": layer.b.copy(),
            })
        return params

    def set_params(self, params):
        for i, layer in enumerate(self.layers):
            layer.W = np.array(params[i]["W"])
            layer.b = np.array(params[i]["b"])


class MultiTaskHead:
    def __init__(self, in_dim: int, task_dims: Dict[str, int]):
        self.heads = {name: SimpleLinear(in_dim, outd) for name, outd in task_dims.items()}

    def forward(self, x):
        return {name: head.forward(x) for name, head in self.heads.items()}

    def backward(self, grads: Dict[str, np.ndarray]):
        # For simplicity, sum gradients if needed
        dx = None
        for name, grad in grads.items():
            g = self.heads[name].backward(grad)
            if dx is None:
                dx = g
            else:
                dx = dx + g
        return dx
