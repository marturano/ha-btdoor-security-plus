"""Regression tests for Call Journal beta.2.1 consistency fixes."""
from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"

# Build only the package fragments needed by the unit under test, avoiding the
# Home Assistant integration entrypoint and its external dependencies.
for name, path in (
    ("custom_components", ROOT / "custom_components"),
    ("custom_components.btdoor_security_plus", PKG),
    ("custom_components.btdoor_security_plus.event_bus", PKG / "event_bus"),
    ("custom_components.btdoor_security_plus.call_journal", PKG / "call_journal"),
):
    module = ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module

ha = ModuleType("homeassistant")
helpers = ModuleType("homeassistant.helpers")
storage = ModuleType("homeassistant.helpers.storage")
class Store:
    def __class_getitem__(cls, item):
        return cls
storage.Store = Store
sys.modules["homeassistant"] = ha
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.storage"] = storage

def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

events = load("custom_components.btdoor_security_plus.event_bus.events", PKG / "event_bus" / "events.py")
sys.modules["custom_components.btdoor_security_plus.event_bus"].RuntimeEvent = events.RuntimeEvent
sys.modules["custom_components.btdoor_security_plus.event_bus"].RuntimeEventType = events.RuntimeEventType
journal_module = load("custom_components.btdoor_security_plus.call_journal.journal", PKG / "call_journal" / "journal.py")

CallJournal = journal_module.CallJournal
RuntimeEvent = events.RuntimeEvent
RuntimeEventType = events.RuntimeEventType
RuntimeSource = events.RuntimeSource

class FakeStore:
    def __init__(self, value=None):
        self.value = value
        self.saved = None
    async def async_load(self):
        return self.value
    async def async_save(self, value):
        self.saved = value
    def async_delay_save(self, callback, delay):
        self.saved = callback()

def event(kind, call_id, timestamp, **payload):
    return RuntimeEvent(event_type=kind, source=RuntimeSource.DIALOG, payload={"call_id": call_id, **payload}, timestamp=timestamp)

def test_late_duplicate_terminal_event_does_not_reopen_call():
    journal = CallJournal(FakeStore())
    journal.process(event(RuntimeEventType.INVITE_RECEIVED, "abc", "2026-07-18T10:00:00+00:00"))
    journal.process(event(RuntimeEventType.CALL_CANCELLED, "abc", "2026-07-18T10:00:05+00:00", method="CANCEL"))
    journal.process(event(RuntimeEventType.MEDIA_CLOSED, "abc", "2026-07-18T10:00:06+00:00", media_runtime={"closed_at": "2026-07-18T10:00:06+00:00"}))
    journal.process(event(RuntimeEventType.CALL_CANCELLED, "abc", "2026-07-18T10:00:07+00:00"))
    assert journal.metrics["retained_calls"] == 1
    assert journal.metrics["active_calls"] == 0

def test_load_self_heals_ended_active_record():
    record = {"call_id": "abc", "started_at": "2026-07-18T10:00:00+00:00", "ended_at": "2026-07-18T10:00:06+00:00", "result": "missed"}
    journal = CallJournal(FakeStore({"records": [], "active": {"abc": record}}))
    asyncio.run(journal.async_load())
    assert journal.metrics["retained_calls"] == 1
    assert journal.metrics["active_calls"] == 0
