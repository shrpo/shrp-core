import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import asyncio
import pytest
from shrp_ai.pipeline.pipeline import Pipeline
from shrp_ai.context.manager import ContextManager
from shrp_ai.decision.base import DeterministicDecision
from shrp_ai.adapters.base import BaseAdapter, AdapterRegistry
from shrp_ai.resources.manager import ResourceManager
from shrp_ai.modules_demo.sensor import SimulatedSensorModule


def test_pipeline_order():
    ctx_mgr = ContextManager()
    ctx = ctx_mgr.create()
    results = []
    async def s1(c):
        results.append(1)
        return 1
    async def s2(c):
        results.append(2)
        return 2
    pipe = Pipeline([('s1', s1), ('s2', s2)])
    asyncio.get_event_loop().run_until_complete(pipe.execute(ctx))
    assert results == [1, 2]


def test_pipeline_failure():
    ctx_mgr = ContextManager()
    ctx = ctx_mgr.create()
    async def bad(c):
        raise ValueError("fail")
    pipe = Pipeline([('bad', bad)])
    try:
        asyncio.get_event_loop().run_until_complete(pipe.execute(ctx))
        assert False
    except ValueError:
        assert True


def test_context_isolation():
    ctx_mgr = ContextManager()
    c1 = ctx_mgr.create(initial={'x': 1})
    c2 = ctx_mgr.create(initial={'x': 2})
    c1.set('y', 10)
    assert c2.get('y') is None
    assert c1.get('x') == 1 and c2.get('x') == 2


def test_context_updates():
    ctx_mgr = ContextManager()
    c = ctx_mgr.create()
    c.update({'a': 1, 'b': 2})
    assert c.get('a') == 1 and c.get('b') == 2


def test_deterministic_decision():
    dec = DeterministicDecision()
    res = asyncio.get_event_loop().run_until_complete(dec.decide(None, {}, ['log', 'alert']))
    assert res.selected == 'log'


def test_adapter_registry():
    class Dummy(BaseAdapter):
        name = 'dummy'
        version = '0.1.0'
        capabilities = {}
        async def invoke(self, input_data):
            return {'ok': True}
    reg = AdapterRegistry()
    reg.register(Dummy())
    assert reg.get('dummy') is not None


def test_resource_manager():
    rm = ResourceManager()
    info = rm.get_info()
    assert hasattr(info, 'has_gpu')
    assert info.has_gpu is False


def test_simulated_sensor_module():
    mod = SimulatedSensorModule()
    res = asyncio.get_event_loop().run_until_complete(mod.execute({'readings': [1, 2, 3]}))
    assert res['decision']['selected'] in ['log', 'alert', 'ignore']


def test_backward_compat():
    from shrp_ai import CoreEngine
    core = CoreEngine()
    asyncio.get_event_loop().run_until_complete(core.initialize())
    asyncio.get_event_loop().run_until_complete(core.shutdown())
