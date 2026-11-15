from __future__ import annotations

import os
import psutil
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ResourceInfo:
    cpu_count: Optional[int] = None
    memory_total_mb: Optional[float] = None
    memory_available_mb: Optional[float] = None
    has_gpu: bool = False


class ResourceManager:
    def __init__(self, max_memory_mb: Optional[float] = None, max_cpu_percent: Optional[float] = None):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent

    def get_info(self) -> ResourceInfo:
        info = ResourceInfo()
        try:
            info.cpu_count = os.cpu_count()
        except Exception:
            info.cpu_count = None
        try:
            vm = psutil.virtual_memory()
            info.memory_total_mb = vm.total / (1024 * 1024)
            info.memory_available_mb = vm.available / (1024 * 1024)
        except Exception:
            pass
        info.has_gpu = False  # never assume GPU
        return info

    def check_limits(self) -> bool:
        try:
            vm = psutil.virtual_memory()
            if self.max_memory_mb is not None and vm.available < self.max_memory_mb * 1024 * 1024:
                return False
        except Exception:
            pass
        return True
