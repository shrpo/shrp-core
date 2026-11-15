"""SHRP Core v0.3 Performance Baseline Benchmarks (inline)."""
import asyncio
import json
import os
import sys
import time
import statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from shrp_ai import CoreEngine, Request, EventBus, TaskManager
from shrp_ai.context.manager import ContextManager
from shrp_ai.pipeline.pipeline import Pipeline
from shrp_ai.modules_demo.sensor import SimulatedSensorModule


def bench_core_init():
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        core = CoreEngine()
        asyncio.run(core.initialize())
        asyncio.run(core.shutdown())
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "name": "core_init",
        "iterations": len(times),
        "avg_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3),
    }


def bench_request_processing():
    core = CoreEngine()
    asyncio.run(core.initialize())
    times = []
    for i in range(20):
        t0 = time.perf_counter()
        asyncio.run(core.handle_request(Request(f"r{i}", "echo", {"x": i})))
        times.append((time.perf_counter() - t0) * 1000)
    asyncio.run(core.shutdown())
    return {
        "name": "request_processing",
        "iterations": len(times),
        "avg_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3),
    }


def bench_event_bus():
    bus = EventBus()
    received = []

    def cb(data):
        received.append(data)

    bus.subscribe("test", cb)
    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        asyncio.run(bus.publish("test", {"x": 1}))
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "name": "event_bus",
        "iterations": len(times),
        "avg_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3),
    }


def bench_task_manager():
    async def dummy():
        return 1

    tm = TaskManager(max_concurrent=10)
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        tid = asyncio.run(tm.submit(dummy))
        asyncio.run(asyncio.sleep(0.01))
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "name": "task_manager",
        "iterations": len(times),
        "avg_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3),
    }


def bench_context_manager():
    cm = ContextManager()
    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        ctx = cm.create(initial={"x": 1})
        ctx.set("y", 2)
        cm.clear(ctx.request_id)
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "name": "context_manager",
        "iterations": len(times),
        "avg_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3),
    }


def bench_pipeline():
    async def s1(ctx):
        ctx.set("a", 1)
        return 1

    async def s2(ctx):
        ctx.set("b", 2)
        return 2

    pipe = Pipeline([("s1", s1), ("s2", s2)])
    cm = ContextManager()
    times = []
    for _ in range(10):
        ctx = cm.create()
        t0 = time.perf_counter()
        asyncio.run(pipe.execute(ctx))
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "name": "pipeline",
        "iterations": len(times),
        "avg_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3),
    }


def bench_sensor_module():
    mod = SimulatedSensorModule()
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        asyncio.run(mod.execute({"readings": [1, 2, 3]}))
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "name": "sensor_module",
        "iterations": len(times),
        "avg_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 3),
    }


def main():
    results = [
        bench_core_init(),
        bench_request_processing(),
        bench_event_bus(),
        bench_task_manager(),
        bench_context_manager(),
        bench_pipeline(),
        bench_sensor_module(),
    ]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()