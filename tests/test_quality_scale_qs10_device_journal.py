"""QS-10 behavioural coverage for device registry, topology and call journal."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _reset() -> None:
    for name in list(sys.modules):
        if name.startswith("qs10pkg") or name.startswith("homeassistant"):
            sys.modules.pop(name, None)


def _package(name: str, path: Path) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module
    return module


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class DeviceInfo(dict):
    pass


class FakeDevice:
    def __init__(self, id, identifiers, config_entries=("entry",), **kwargs):
        self.id = id
        self.identifiers = set(identifiers)
        self.config_entries = set(config_entries)
        self.name = kwargs.get("name")
        self.name_by_user = kwargs.get("name_by_user")
        self.manufacturer = kwargs.get("manufacturer")
        self.model = kwargs.get("model")
        self.sw_version = kwargs.get("sw_version")
        self.configuration_url = kwargs.get("configuration_url")
        self.via_device_id = kwargs.get("via_device_id")
        self.area_id = kwargs.get("area_id")


class FakeDeviceRegistry:
    def __init__(self):
        self.devices = {}
        self.updated = []
        self.removed = []

    def async_get_device(self, identifiers):
        return next((d for d in self.devices.values() if set(identifiers) <= d.identifiers), None)

    def async_get_or_create(self, **kwargs):
        device = self.async_get_device(kwargs["identifiers"])
        if device is None:
            device = FakeDevice(
                f"dev{len(self.devices) + 1}",
                kwargs["identifiers"],
                config_entries=(kwargs["config_entry_id"],),
                name=kwargs.get("name"),
                manufacturer=kwargs.get("manufacturer"),
                model=kwargs.get("model"),
                sw_version=kwargs.get("sw_version"),
                configuration_url=kwargs.get("configuration_url"),
            )
            self.devices[device.id] = device
        return device

    def async_update_device(self, device_id, **updates):
        self.updated.append((device_id, updates))
        device = self.devices[device_id]
        for key, value in updates.items():
            setattr(device, key, value)

    def async_remove_device(self, device_id):
        self.removed.append(device_id)
        self.devices.pop(device_id, None)


class FakeEntityRegistry:
    def __init__(self):
        self.by_device = {}
        self.removed = []

    def async_remove(self, entity_id):
        self.removed.append(entity_id)


def _load_device_modules(registry, entity_registry):
    _reset()
    _package("qs10pkg", PKG)
    _package("qs10pkg.device_model", PKG / "device_model")
    _package("qs10pkg.managers", PKG / "managers")
    _package("qs10pkg.models", PKG / "models")
    _package("qs10pkg.visibility", PKG / "visibility")

    _package("homeassistant", Path("."))
    helpers = _package("homeassistant.helpers", Path("."))
    dr = types.ModuleType("homeassistant.helpers.device_registry")
    dr.DeviceInfo = DeviceInfo
    dr.async_get = lambda hass: registry
    er = types.ModuleType("homeassistant.helpers.entity_registry")
    er.async_get = lambda hass: entity_registry
    er.async_entries_for_device = lambda reg, device_id, include_disabled_entities=True: list(
        reg.by_device.get(device_id, [])
    )
    sys.modules[dr.__name__] = dr
    sys.modules[er.__name__] = er
    helpers.device_registry = dr
    helpers.entity_registry = er

    _load("qs10pkg.const", PKG / "const.py")
    factory = _load("qs10pkg.device_model.factory", PKG / "device_model" / "factory.py")
    _load("qs10pkg.device_model.names", PKG / "device_model" / "names.py")
    vismod = _load("qs10pkg.visibility.manager", PKG / "visibility" / "manager.py")
    vispkg = sys.modules["qs10pkg.visibility"]
    vispkg.visibility_for_entry = vismod.visibility_for_entry
    _load("qs10pkg.models.device", PKG / "models" / "device.py")
    _load("qs10pkg.managers.language_manager", PKG / "managers" / "language_manager.py")
    _load("qs10pkg.managers.device_name_provider", PKG / "managers" / "device_name_provider.py")
    manager = _load("qs10pkg.device_model.manager", PKG / "device_model" / "manager.py")
    facade = _load("qs10pkg.managers.device_manager", PKG / "managers" / "device_manager.py")
    return factory, manager, facade


@pytest.mark.asyncio
async def test_device_registration_removes_hidden_and_migrates_metadata():
    registry = FakeDeviceRegistry()
    entities = FakeEntityRegistry()
    factory, manager, _ = _load_device_modules(registry, entities)
    entry = SimpleNamespace(
        entry_id="entry",
        unique_id="root",
        runtime_data=SimpleNamespace(language="it"),
        data={"device_name": "Porta", "gateway_id": "GW1"},
        options={
            "show_cloud_status": False,
            "show_sip_monitor": True,
            "show_call_monitor": True,
            "show_media_monitor": True,
            "developer_mode": False,
            "show_advanced_diagnostics": False,
            "quick_voice_gate": True,
        },
    )
    hidden_id = factory.device_identifier(entry, factory.DeviceKind.CLOUD)
    hidden = FakeDevice("hidden", {hidden_id}, name="Cloud")
    registry.devices[hidden.id] = hidden
    entities.by_device[hidden.id] = [
        SimpleNamespace(entity_id="sensor.hidden", config_entry_id="entry")
    ]

    gateway_id = factory.device_identifier(entry, factory.DeviceKind.GATEWAY)
    gateway = FakeDevice(
        "gateway", {gateway_id}, name="Old", manufacturer="Wrong", model="Wrong", sw_version="0"
    )
    registry.devices[gateway.id] = gateway

    await manager.async_register_devices(object(), entry)
    assert "hidden" in registry.removed and "sensor.hidden" in entities.removed
    assert gateway.name == "Porta"
    assert gateway.manufacturer == factory.MANUFACTURER
    assert len(registry.devices) == 5

    report = manager.device_registry_report(object(), entry)
    assert report["device_count"] == 5 and report["resolved_language"] == "it"
    translation = manager.device_translation_report(entry)
    assert translation["device_names"]["cloud"] == "Stato Cloud"
    entry.runtime_data.language = "xx-YY"
    assert manager.device_translation_report(entry)["fallback_to_english"] is True


def test_device_topology_validation_reports_missing_duplicates_and_areas(monkeypatch):
    registry = FakeDeviceRegistry()
    entities = FakeEntityRegistry()
    factory, _, facade = _load_device_modules(registry, entities)
    entry = SimpleNamespace(
        entry_id="entry",
        unique_id="root",
        runtime_data=SimpleNamespace(language="en"),
        data={},
        options={},
    )
    gateway_identifier = factory.device_identifier(entry, factory.DeviceKind.GATEWAY)
    expected = factory.device_info_for(entry, factory.DeviceKind.GATEWAY)
    root = FakeDevice(
        "root",
        {gateway_identifier},
        name=expected["name"],
        manufacturer="Wrong",
        model=expected["model"],
        sw_version=expected["sw_version"],
        area_id="front",
    )
    duplicate = FakeDevice(
        "root2",
        {gateway_identifier},
        name=expected["name"],
        manufacturer=expected["manufacturer"],
        model=expected["model"],
        sw_version=expected["sw_version"],
        name_by_user=" ",
    )
    registry.devices = {root.id: root, duplicate.id: duplicate}
    manager = facade.DeviceManager(object(), entry)
    report = manager.validate_topology()
    assert report.valid is False
    assert "gateway" in report.duplicate_devices
    assert report.missing_devices
    assert report.metadata_mismatches
    assert report.user_names_preserved is False
    assert "gateway" in report.devices_with_area
    assert report.as_dict()["expected_count"] == len(factory.DeviceKind)


class FakeStore:
    def __init__(self, value=None):
        self.value = value
        self.saved = None
        self.delayed = 0

    async def async_load(self):
        return self.value

    async def async_save(self, value):
        self.saved = value

    def async_delay_save(self, callback, delay):
        self.delayed += 1
        self.saved = callback()


def _load_journal():
    _reset()
    _package("qs10pkg", PKG)
    _package("qs10pkg.event_bus", PKG / "event_bus")
    _package("qs10pkg.call_journal", PKG / "call_journal")
    _package("homeassistant", Path("."))
    _package("homeassistant.helpers", Path("."))
    storage = types.ModuleType("homeassistant.helpers.storage")

    class Store:
        def __class_getitem__(cls, item):
            return cls

    storage.Store = Store
    sys.modules[storage.__name__] = storage
    events = _load("qs10pkg.event_bus.events", PKG / "event_bus" / "events.py")
    buspkg = sys.modules["qs10pkg.event_bus"]
    buspkg.RuntimeEvent = events.RuntimeEvent
    buspkg.RuntimeEventType = events.RuntimeEventType
    journal = _load("qs10pkg.call_journal.journal", PKG / "call_journal" / "journal.py")
    return journal, events


def _event(events, kind, call_id="c1", timestamp="2026-07-23T10:00:00+00:00", **payload):
    return events.RuntimeEvent(
        event_type=kind,
        source=events.RuntimeSource.DIALOG,
        payload={"call_id": call_id, **payload},
        timestamp=timestamp,
    )


@pytest.mark.asyncio
async def test_call_journal_full_lifecycle_metrics_rebuild_and_clear():
    journal_mod, events = _load_journal()
    store = FakeStore()
    journal = journal_mod.CallJournal(store, max_records=3)
    callbacks = []
    bus = SimpleNamespace(subscribe=lambda cb: callbacks.append(cb) or (lambda: callbacks.clear()))
    journal.attach(bus)
    journal.attach(bus)
    assert len(callbacks) == 1
    journal.process(_event(events, events.RuntimeEventType.INVITE_RECEIVED, caller="door"))
    journal.process(
        _event(
            events,
            events.RuntimeEventType.MEDIA_PREPARED,
            media_runtime={
                "plan": {
                    "audio": {"codec": "PCMU"},
                    "video": {"codec": "H264"},
                    "srtp": {"suite": "AES"},
                }
            },
        )
    )
    journal.process(_event(events, events.RuntimeEventType.CALL_ANSWERED))
    journal.process(
        _event(
            events,
            events.RuntimeEventType.MEDIA_CLOSED,
            timestamp="2026-07-23T10:00:12+00:00",
            media_runtime={"closed_at": "2026-07-23T10:00:12+00:00", "close_reason": "normal"},
        )
    )
    metrics = journal.metrics
    assert metrics["retained_calls"] == 1 and metrics["active_calls"] == 0
    assert metrics["average_duration_seconds"] == 12.0
    assert metrics["audio_codec_usage"] == {"PCMU": 1}
    assert journal.last_record["result"] == "answered"
    journal.detach()
    assert callbacks == []

    await journal.async_rebuild(
        [
            _event(events, events.RuntimeEventType.CALL_STARTED, "c2"),
            _event(events, events.RuntimeEventType.CALL_CANCELLED, "c2", method="CANCEL"),
            _event(events, events.RuntimeEventType.CALL_ENDED, "c2", "2026-07-23T10:00:05+00:00"),
        ]
    )
    assert journal.last_record["result"] == "missed"
    assert store.saved["records"]
    await journal.async_clear()
    assert journal.records == [] and store.saved["active"] == {}


@pytest.mark.asyncio
async def test_call_journal_load_self_heals_and_ignores_invalid_events():
    journal_mod, events = _load_journal()
    ended = {
        "call_id": "done",
        "started_at": "bad",
        "ended_at": "2026-07-23T10:00:00+00:00",
        "result": "missed",
    }
    active = {
        "call_id": "live",
        "started_at": "2026-07-23T10:00:00+00:00",
        "ended_at": None,
        "result": "ringing",
    }
    store = FakeStore(
        {"records": ["bad", ended], "active": {"done": ended, "live": active, "junk": "bad"}}
    )
    journal = journal_mod.CallJournal(store)
    await journal.async_load()
    assert journal.metrics["retained_calls"] == 1 and journal.metrics["active_calls"] == 1
    journal.process(_event(events, events.RuntimeEventType.CALL_ENDED, call_id=""))
    journal.process(_event(events, events.RuntimeEventType.CALL_REJECTED, call_id="unknown"))
    journal.process(
        _event(
            events,
            events.RuntimeEventType.MEDIA_FAILED,
            call_id="live",
            error="boom",
            timestamp="2026-07-23T10:00:01+00:00",
        )
    )
    assert journal.last_record["result"] == "failed"
    assert journal_mod._iso_duration("bad", "also-bad") is None
