"""QS-14 behavioural coverage for core runtime, dispatcher and event bus."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _reset() -> None:
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus"):
            sys.modules.pop(name, None)
    root = types.ModuleType("custom_components")
    root.__path__ = [str(ROOT / "custom_components")]
    pkg = types.ModuleType("custom_components.btdoor_security_plus")
    pkg.__path__ = [str(PKG)]
    sys.modules[root.__name__] = root
    sys.modules[pkg.__name__] = pkg


def _pkg(name: str) -> None:
    full = f"custom_components.btdoor_security_plus.{name}"
    path = PKG.joinpath(*name.split("."))
    mod = types.ModuleType(full)
    mod.__path__ = [str(path)]
    sys.modules[full] = mod


def _load(name: str):
    full = f"custom_components.btdoor_security_plus.{name}"
    path = PKG.joinpath(*name.split("."))
    if path.is_dir():
        path = path / "__init__.py"
    else:
        path = path.with_suffix(".py")
    spec = importlib.util.spec_from_file_location(
        full,
        path,
        submodule_search_locations=[str(path.parent)] if path.name == "__init__.py" else None,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def modules():
    previous = {
        n: m
        for n, m in sys.modules.items()
        if n.startswith("custom_components.btdoor_security_plus")
    }
    _reset()
    _pkg("event_bus")
    _pkg("core")
    events = _load("event_bus.events")
    bus = _load("event_bus.bus")
    lifecycle = _load("core.lifecycle")
    runtime = _load("core.runtime")
    event_pkg = sys.modules["custom_components.btdoor_security_plus.event_bus"]
    for attr in ("RuntimeEvent", "RuntimeEventType"):
        setattr(event_pkg, attr, getattr(events, attr))
    event_pkg.RuntimeEventBus = bus.RuntimeEventBus
    dispatcher = _load("core.dispatcher")
    try:
        yield SimpleNamespace(
            events=events, bus=bus, lifecycle=lifecycle, runtime=runtime, dispatcher=dispatcher
        )
    finally:
        for n in list(sys.modules):
            if n.startswith("custom_components.btdoor_security_plus"):
                sys.modules.pop(n, None)
        sys.modules.update(previous)


class StoreStub:
    def __init__(self, payload=None):
        self.payload = payload
        self.saved = []

    async def async_load(self):
        return self.payload

    def async_delay_save(self, callback, delay):
        self.saved.append((callback, delay))


@pytest.mark.asyncio
async def test_event_bus_load_publish_subscribe_eviction(modules):
    e = modules.events
    valid = e.RuntimeEvent(e.RuntimeEventType.SIP_REGISTERED, e.RuntimeSource.SIP).as_dict()
    store = StoreStub({"events": [valid, {"event_type": "invalid"}, 7]})
    bus = modules.bus.RuntimeEventBus(store, max_events=2)
    await bus.async_load()
    assert bus.retained_count == 1
    all_seen, typed_seen = [], []
    remove_all = bus.subscribe(all_seen.append)
    remove_typed = bus.subscribe(typed_seen.append, e.RuntimeEventType.CALL_STARTED)
    first = e.RuntimeEvent(e.RuntimeEventType.CALL_STARTED, e.RuntimeSource.DIALOG)
    second = e.RuntimeEvent(e.RuntimeEventType.CALL_ENDED, e.RuntimeSource.DIALOG)
    bus.publish(first)
    bus.publish(second)
    assert all_seen == [first, second] and typed_seen == [first]
    assert bus.metrics["events_by_type"] == {"call_started": 1, "call_ended": 1}
    assert bus.metrics["events_by_source"] == {"dialog": 2}
    assert bus.compact_history(0) == []
    assert bus.compact_history(1)[0]["type"] == "call_ended"
    assert store.saved[-1][0]() == bus.export_state()
    remove_all()
    remove_typed()
    bus.publish(e.RuntimeEvent(e.RuntimeEventType.GATE_OPENED, e.RuntimeSource.INTEGRATION))
    assert all_seen == [first, second]


@pytest.mark.asyncio
async def test_event_bus_empty(modules):
    bus = modules.bus.RuntimeEventBus(StoreStub(None), max_events=1)
    await bus.async_load()
    assert bus.history == [] and bus.last_event_summary is None


@pytest.mark.asyncio
async def test_runtime_happy_restart_and_diagnostics(modules):
    state = modules.lifecycle.LifecycleState
    runtime = modules.runtime.BTDoorPlatformRuntime(metadata={"phase": "qs14"})
    calls = []

    async def s1():
        calls.append("s1")

    async def t1():
        calls.append("t1")

    async def s2():
        calls.append("s2")

    async def t2():
        calls.append("t2")

    runtime.register(start=s1, stop=t1)
    runtime.register(start=s2, stop=t2)
    await runtime.async_start()
    await runtime.async_start()
    assert runtime.state is state.RUNNING and calls == ["s1", "s2"]
    assert runtime.diagnostics()["subsystem_count"] == 2
    with pytest.raises(RuntimeError):
        runtime.register(start=s1, stop=t1)
    await runtime.async_stop()
    assert calls[-2:] == ["t2", "t1"]
    await runtime.async_start()
    assert runtime.state is state.RUNNING


@pytest.mark.asyncio
async def test_runtime_rollback_invalid_state_and_stop_errors(modules):
    state = modules.lifecycle.LifecycleState
    stopped = []

    async def good():
        return None

    async def fail_start():
        raise ValueError("boom")

    async def stop_good():
        stopped.append("ok")

    async def stop_bad():
        raise RuntimeError("stop")

    runtime = modules.runtime.BTDoorPlatformRuntime()
    runtime.register(start=good, stop=stop_good)
    runtime.register(start=fail_start, stop=stop_bad)
    with pytest.raises(ValueError):
        await runtime.async_start()
    assert runtime.state is state.FAILED and stopped == ["ok"]
    runtime2 = modules.runtime.BTDoorPlatformRuntime()
    runtime2.register(start=good, stop=stop_bad)
    await runtime2.async_start()
    with pytest.raises(ExceptionGroup):
        await runtime2.async_stop()
    assert runtime2.state is state.FAILED
    runtime3 = modules.runtime.BTDoorPlatformRuntime()
    await runtime3.async_stop()
    runtime3.state = state.STARTING
    with pytest.raises(RuntimeError):
        await runtime3.async_start()


def test_dispatcher_facade(modules):
    fake = SimpleNamespace(publish=Mock(), subscribe=Mock(return_value=lambda: None))
    dispatcher = modules.dispatcher.RuntimeDispatcher(fake)
    event = modules.events.RuntimeEvent(
        modules.events.RuntimeEventType.RUNTIME_EVENT, modules.events.RuntimeSource.INTEGRATION
    )
    dispatcher.publish(event)
    fake.publish.assert_called_once_with(event)
    assert callable(
        dispatcher.subscribe(lambda _: None, modules.events.RuntimeEventType.RUNTIME_EVENT)
    )
    assert dispatcher.event_bus is fake


def test_lazy_manager_exports():
    previous = {
        n: m
        for n, m in sys.modules.items()
        if n.startswith("custom_components.btdoor_security_plus")
    }
    _reset()
    managers = _load("managers")
    sentinel = object()
    managers.import_module = lambda _: SimpleNamespace(VisibilityManager=sentinel)
    assert managers.VisibilityManager is sentinel
    with pytest.raises(AttributeError):
        _ = managers.Missing
    for n in list(sys.modules):
        if n.startswith("custom_components.btdoor_security_plus"):
            sys.modules.pop(n, None)
    sys.modules.update(previous)
