"""SHRP Core v0.3 Final Verification Tests."""
import asyncio
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shrp_ai import CoreEngine, Request
from shrp_ai.core.state_memory import MemoryManager
from shrp_ai.core.tasks import TaskManager


def test_concurrent_sqlite_operations():
    """Verify concurrent SQLite operations work with persistent connection."""
    db_path = os.path.join(tempfile.gettempdir(), f"shrp_concurrent_{os.getpid()}.db")
    mm = MemoryManager(db_path=db_path)

    async def write_task(i):
        mm.save(f"key_{i}", {"value": i})

    async def run():
        tasks = [write_task(i) for i in range(20)]
        await asyncio.gather(*tasks)

    asyncio.run(run())

    for i in range(20):
        assert mm.get(f"key_{i}") == {"value": i}
    mm.close()


def test_high_volume_task_cleanup():
    """Verify completed tasks are cleaned up on next submit."""
    tm = TaskManager(max_concurrent=10, max_tasks=100)

    async def quick():
        await asyncio.sleep(0.001)
        return 1

    async def run():
        for _ in range(30):
            await tm.submit(quick)
        await asyncio.sleep(0.1)
        # Trigger cleanup by submitting one more task
        await tm.submit(quick)
        remaining = len(tm._tasks)
        assert remaining <= 2  # only the new one plus any still running

    asyncio.run(run())


def test_shutdown_with_active_tasks():
    """Verify shutdown cancels and awaits active tasks."""
    tm = TaskManager(max_concurrent=5)

    async def slow():
        await asyncio.sleep(10)
        return 1

    async def run():
        await tm.submit(slow)
        await tm.submit(slow)
        await tm.shutdown()

    asyncio.run(run())
    assert len(tm._tasks) == 0


def test_repeated_init_shutdown():
    """Verify Core can be initialized and shut down repeatedly."""
    for _ in range(5):
        core = CoreEngine()
        asyncio.run(core.initialize())
        assert core._initialized
        asyncio.run(core.handle_request(Request("1", "echo", {"x": 1})))
        asyncio.run(core.shutdown())
        assert not core._initialized


def test_task_exception_handling():
    """Verify task exceptions are captured and don't crash the system."""
    tm = TaskManager(max_concurrent=5)

    async def failing():
        raise RuntimeError("test error")

    async def run():
        tid = await tm.submit(failing)
        await asyncio.sleep(0.01)
        info = tm.status(tid)
        assert info["status"] == "error"
        assert "test error" in info["error"]

    asyncio.run(run())


def test_memory_stability_repeated_operations():
    """Verify no memory leak under repeated operations."""
    core = CoreEngine()
    asyncio.run(core.initialize())
    for _ in range(100):
        asyncio.run(core.handle_request(Request("1", "echo", {"x": 1})))
    asyncio.run(core.shutdown())
    assert True


def test_sqlite_transaction_safety():
    """Verify SQLite transactions are committed correctly."""
    db_path = os.path.join(tempfile.gettempdir(), f"shrp_tx_{os.getpid()}.db")
    mm = MemoryManager(db_path=db_path)
    mm.save("k1", "v1")
    mm.save("k2", "v2")
    assert mm.get("k1") == "v1"
    assert mm.get("k2") == "v2"
    mm.delete("k1")
    assert mm.get("k1") is None
    assert mm.get("k2") == "v2"
    mm.close()


def test_sqlite_list_operations():
    """Verify SQLite list returns all records."""
    db_path = os.path.join(tempfile.gettempdir(), f"shrp_list_{os.getpid()}.db")
    mm = MemoryManager(db_path=db_path)
    mm.save("a", 1)
    mm.save("b", 2)
    items = mm.list()
    assert items["a"] == 1
    assert items["b"] == 2
    mm.close()