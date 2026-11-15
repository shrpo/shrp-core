from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np


def to_numpy(x) -> np.ndarray:
    if isinstance(x, np.ndarray):
        return x
    try:
        import torch

        if isinstance(x, torch.Tensor):
            return x.detach().cpu().numpy()
    except Exception:
        pass
    return np.array(x)


def from_numpy(x: np.ndarray):
    try:
        import torch

        return torch.from_numpy(x)
    except Exception:
        return x


def ensure_shape(x: np.ndarray, shape: Tuple[int, ...]) -> np.ndarray:
    x = np.asarray(x)
    if x.shape != shape:
        raise ValueError(f"shape mismatch: got {x.shape}, expected {shape}")
    return x


def batch_iter(data: np.ndarray, batch_size: int, shuffle: bool = False):
    n = len(data)
    indices = np.arange(n)
    if shuffle:
        np.random.shuffle(indices)
    for i in range(0, n, batch_size):
        batch_idx = indices[i : i + batch_size]
        yield batch_idx
