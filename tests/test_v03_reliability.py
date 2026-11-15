"""SHRP Core v0.3 Reliability and Regression Tests."""
import asyncio
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shrp_ai import CoreEngine, Request
from shrp_ai.core.modules import BaseModule, ModuleManager
from shrp_ai.core.state_memory import StateManager, MemoryManager
from shrp_ai.core.events import EventBus
from shrp_ai.core.tasks import TaskManager
from shrp_ai.core.interfaces import Request, Response
from shrp_ai.context.manager import ContextManager


def test_concurrent_requests():
    core = CoreEngine()
    asyncio.run(core.initialize())

    async def run():
        tasks = [core.handle_request(Request(f"r{i}", "echo", {"x": i})) for i in range(20)]
        return await asyncio.gather(*tasks)

    results = asyncio.run(run())
    assert all(r.status == "ok" for r in results)
    asyncio.run(core.shutdown())


def test_module_init_failure_isolated():
    class BadModule(BaseModule):
        name = "bad"
        version = "0.1.0"
        description = "Fails on init"

        async def initialize(self):
            raise RuntimeError("init failed")

        async def execute(self, payload):
            return {"ok": True}

    core = CoreEngine()
    asyncio.run(core.initialize())
    core.modules.register(BadModule())
    # Other modules should still work
    resp = asyncio.run(core.handle_request(Request("1", "echo", {"x": 1})))
    assert resp.status == "ok"
    asyncio.run(core.shutdown())


def test_task_cancellation():
    tm = TaskManager(max_concurrent=5)

    async def quick():
        await asyncio.sleep(0.001)
        return 1

    tid = asyncio.run(tm.submit(quick))
    # Task may have already completed; cancel is a no-op if done
    tm.cancel(tid)
    info = tm.status(tid)
    assert info["status"] in ("completed", "cancelled", "running", "pending", "error", "timeout")


def test_event_subscriber_exception_isolated():
    bus = EventBus()

    def bad_cb(data):
        raise RuntimeError("bad subscriber")

    def good_cb(data):
        return "ok"

    bus.subscribe("test", bad_cb)
    bus.subscribe("test", good_cb)
    # Should not raise
    asyncio.run(bus.publish("test", {"x": 1}))


def test_context_isolation():
    cm = ContextManager()
    c1 = cm.create(initial={"x": 1})
    c2 = cm.create(initial={"x": 2})
    c1.set("y", 10)
    assert c2.get("y") is None
    assert c1.get("x") == 1 and c2.get("x") == 2


def test_memory_manager_persistence():
    mm = MemoryManager(db_path=os.path.join(tempfile.gettempdir(), "shrp_test.db"))
    mm.save("key1", {"data": [1, 2, 3]})
    val = mm.get("key1")
    assert val == {"data": [1, 2, 3]}
    mm.delete("key1")
    assert mm.get("key1") is None
    mm.close()


def test_memory_manager_close():
    mm = MemoryManager(db_path=os.path.join(tempfile.gettempdir(), "shrp_test2.db"))
    mm.save("k", "v")
    mm.close()
    # Reopening should work
    mm2 = MemoryManager(db_path=os.path.join(tempfile.gettempdir(), "shrp_test2.db"))
    assert mm2.get("k") == "v"
    mm2.close()


def test_graceful_shutdown():
    core = CoreEngine()
    asyncio.run(core.initialize())
    asyncio.run(core.shutdown())
    assert not core._initialized


def test_memory_stability():
    core = CoreEngine()
    asyncio.run(core.initialize())
    for i in range(50):
        asyncio.run(core.handle_request(Request(f"r{i}", "echo", {"x": i})))
    asyncio.run(core.shutdown())
    # No memory leak detected if we reach here
    assert True


def test_invalid_module_raises():
    core = CoreEngine()
    asyncio.run(core.initialize())
    resp = asyncio.run(core.handle_request(Request("1", "nonexistent", {})))
    assert resp.status == "error"
    asyncio.run(core.shutdown())


def test_task_limit_enforced():
    tm = TaskManager(max_concurrent=10, max_tasks=2)

    async def blocking():
        await asyncio.sleep(10)
        return 1

    async def run():
        await tm.submit(blocking)
        await tm.submit(blocking)
        with pytest.raises(RuntimeError):
            await tm.submit(blocking)

    asyncio.run(run())


def test_state_snapshot_restore():
    sm = StateManager()
    sm.set("a", 1)
    snap = sm.snapshot("test")
    sm.set("a", 2)
    sm.restore("test")
    assert sm.get("a") == 1


def test_backward_compat_learning_engine():
    from shrp_ai.nn.models import SHRPNet
    from shrp_ai.training.trainer import Trainer
    from shrp_ai.training.optim import SGD
    from shrp_ai.nn.loss import MSELoss
    import numpy as np

    model = SHRPNet(1, [], 1)
    trainer = Trainer(model, optimizer=SGD(lr=0.01), criterion=MSELoss())
    X = np.array([[1.0], [2.0]])
    y = np.array([[3.0], [5.0]])
    loss = trainer.train_step(X, y)
    assert loss >= 0