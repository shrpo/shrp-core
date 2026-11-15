from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryStats:
    total_mb: float
    available_mb: float
    used_mb: float
    percent_used: float


def get_memory_stats() -> MemoryStats:
    try:
        import psutil

        vm = psutil.virtual_memory()
        total_mb = vm.total / (1024 * 1024)
        available_mb = vm.available / (1024 * 1024)
        used_mb = vm.used / (1024 * 1024)
        percent_used = vm.percent
        return MemoryStats(total_mb, available_mb, used_mb, percent_used)
    except Exception:
        return MemoryStats(0, 0, 0, 0)


def log_memory(prefix: str = "MEM") -> None:
    stats = get_memory_stats()
    print(f"[{prefix}] used={stats.used_mb:.1f}MB avail={stats.available_mb:.1f}MB ({stats.percent_used:.1f}%)")
