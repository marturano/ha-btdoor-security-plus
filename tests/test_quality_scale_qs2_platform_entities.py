"""QS-2 behavioural coverage for entity platforms without a full HA runtime."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "custom_components" / "btdoor_security_plus"


class _Entity:
    def __init_subclass__(cls, **kwargs):
        return super().__init_subclass__()

    def async_on_remove(self, callback):
        self._remove_callback = callback

    async def async_added_to_hass(self):
        return None

    def async_write_ha_state(self):
        return None


class _EventEntity(_Entity):
    def _trigger_event(self, event_type, data):
        self._last_event = (event_type, data)


class HomeAssistantError(Exception):
    def __init__(
        self,
        message=None,
        *,
        translation_domain=None,
        translation_key=None,
        translation_placeholders=None,
    ):
        self.translation_domain = translation_domain
        self.translation_key = translation_key
        self.translation_placeholders = translation_placeholders or {}
        rendered = message or self.translation_placeholders.get("error") or translation_key or ""
        super().__init__(rendered)


class ServiceValidationError(HomeAssistantError):
    pass


def _install_stubs() -> None:
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus"):
            sys.modules.pop(name)

    root_pkg = types.ModuleType("custom_components")
    root_pkg.__path__ = [str(ROOT / "custom_components")]
    sys.modules["custom_components"] = root_pkg

    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG_DIR)]
    package.BticinoConfigEntry = object
    sys.modules["custom_components.btdoor_security_plus"] = package

    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    helpers = types.ModuleType("homeassistant.helpers")
    sys.modules.update(
        {
            "homeassistant": ha,
            "homeassistant.components": components,
            "homeassistant.helpers": helpers,
        }
    )

    for component, class_name, cls in (
        ("binary_sensor", "BinarySensorEntity", _Entity),
        ("button", "ButtonEntity", _Entity),
        ("event", "EventEntity", _EventEntity),
        ("switch", "SwitchEntity", _Entity),
    ):
        module = types.ModuleType(f"homeassistant.components.{component}")
        setattr(module, class_name, cls)
        sys.modules[module.__name__] = module
        setattr(components, component, module)

    persistent = types.ModuleType("homeassistant.components.persistent_notification")
    persistent.async_create = lambda *args, **kwargs: None
    sys.modules[persistent.__name__] = persistent
    components.persistent_notification = persistent

    config_entries = types.ModuleType("homeassistant.config_entries")
    config_entries.ConfigEntry = object
    sys.modules[config_entries.__name__] = config_entries

    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    sys.modules[core.__name__] = core

    exceptions = types.ModuleType("homeassistant.exceptions")
    exceptions.HomeAssistantError = HomeAssistantError
    sys.modules[exceptions.__name__] = exceptions

    const = types.ModuleType("homeassistant.const")
    const.EntityCategory = SimpleNamespace(DIAGNOSTIC="diagnostic")
    sys.modules[const.__name__] = const

    entity = types.ModuleType("homeassistant.helpers.entity")
    entity.Entity = _Entity
    entity.EntityCategory = SimpleNamespace(DIAGNOSTIC="diagnostic")
    sys.modules[entity.__name__] = entity

    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    entity_platform.AddConfigEntryEntitiesCallback = object
    sys.modules[entity_platform.__name__] = entity_platform

    registry = types.ModuleType("homeassistant.helpers.device_registry")
    registry.DeviceInfo = dict
    sys.modules[registry.__name__] = registry


def _load(name: str):
    full_name = f"custom_components.btdoor_security_plus.{name.replace(chr(47), chr(46))}"
    file_path = PKG_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_install_stubs()
const = _load("const")
device_model = _load("device_model/factory")
# expose the public names expected by entity platforms
model_pkg = types.ModuleType("custom_components.btdoor_security_plus.device_model")
model_pkg.__path__ = [str(PKG_DIR / "device_model")]
model_pkg.DeviceKind = device_model.DeviceKind
model_pkg.device_info_for = device_model.device_info_for
sys.modules[model_pkg.__name__] = model_pkg
visibility_manager = _load("visibility/manager")
visibility_pkg = types.ModuleType("custom_components.btdoor_security_plus.visibility")
visibility_pkg.__path__ = [str(PKG_DIR / "visibility")]
visibility_pkg.visibility_for_entry = visibility_manager.visibility_for_entry
sys.modules[visibility_pkg.__name__] = visibility_pkg
entity_base = _load("entity")
binary_sensor = _load("binary_sensor")
button = _load("button")
diagnostics = _load("diagnostics")
event = _load("event")
switch = _load("switch")


def _client(**overrides):
    defaults = dict(
        registered=True,
        last_status="200 OK",
        ringing=False,
        last_caller="Door station",
        last_call_id="call-1",
        media_runtime_state="prepared",
        last_completed_media_session={"closed_reason": "cancel"},
        call_state="idle",
        last_error=None,
        server="sip.example.test",
        port=5060,
        target_uri="sip:door@example.test",
        call_started_at=None,
        call_ended_at=None,
        last_call_duration=0.0,
        call_count=2,
        missed_call_count=1,
        last_message=None,
        last_message_at=None,
        message_count=0,
        last_event_type=None,
        last_event_at=None,
        connected_at=None,
        last_keepalive_at=None,
        reconnect_count=0,
        last_command_duration=None,
        last_command_at=None,
        dialog_state="idle",
        last_sip_method=None,
        last_sdp_offer=None,
        last_info_body=None,
        last_notify_event=None,
        last_refer_to=None,
        media_runtime={},
        media_instrumentation={},
        sip_dispatcher_diagnostics={},
        last_caller_uri=None,
        last_caller_domain=None,
        last_caller_display_name=None,
        add_listener=lambda callback: lambda: None,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _entry(*, quick_voice=True, client=None, developer=None):
    cloud = SimpleNamespace(connected=True)
    dialog_api = SimpleNamespace(state="active")
    return SimpleNamespace(
        unique_id="entry-uid",
        entry_id="entry-id",
        data={},
        options={const.CONF_QUICK_VOICE_GATE: quick_voice},
        runtime_data=SimpleNamespace(
            client=client or _client(),
            api=SimpleNamespace(cloud=lambda: cloud, dialog=lambda: dialog_api),
            developer=developer,
            debug=None,
            last_open=None,
            last_result=None,
            language="en",
        ),
    )


def _attach_hass(entity, response=None):
    services = SimpleNamespace(async_call=AsyncMock(return_value=response))
    entity.hass = SimpleNamespace(services=services)
    entity._context = None
    return services


def test_binary_sensor_properties_and_setup(monkeypatch):
    entry = _entry()
    sensors = [
        binary_sensor.BticinoSipRegisteredSensor(entry),
        binary_sensor.BticinoRingingSensor(entry),
        binary_sensor.BTDoorMediaReadySensor(entry),
        binary_sensor.BTDoorLastCallMissedSensor(entry),
        binary_sensor.BTDoorRuntimeHealthySensor(entry),
        binary_sensor.BTDoorCloudConnectedSensor(entry),
        binary_sensor.BTDoorDialogCallActiveSensor(entry),
    ]
    assert sensors[0].is_on and sensors[0].extra_state_attributes["last_sip_status"] == "200 OK"
    assert sensors[1].is_on is False and sensors[1].extra_state_attributes["call_id"] == "call-1"
    assert (
        sensors[2].is_on
        and sensors[3].is_on
        and sensors[4].is_on
        and sensors[5].is_on
        and sensors[6].is_on
    )
    entry.runtime_data.client.registered = False
    entry.runtime_data.client.last_error = "failed"
    entry.runtime_data.client.media_runtime_state = "failed"
    entry.runtime_data.client.last_completed_media_session = {}
    entry.runtime_data.client.call_state = "connected"
    entry.runtime_data.api.dialog().state = "closed"
    assert not sensors[3].is_on and not sensors[4].is_on and not sensors[6].is_on

    added = []
    monkeypatch.setattr(
        binary_sensor,
        "visibility_for_entry",
        lambda _: SimpleNamespace(filter_entities=lambda value: value[:2]),
    )
    asyncio.run(binary_sensor.async_setup_entry(SimpleNamespace(), entry, added.extend))
    assert len(added) == 2


def test_event_setup_and_filtering(monkeypatch):
    added = []
    entry = _entry()
    asyncio.run(event.async_setup_entry(SimpleNamespace(), entry, added.extend))
    entity = added[0]
    calls, writes = [], []
    monkeypatch.setattr(entity, "_trigger_event", lambda kind, data: calls.append((kind, data)))
    monkeypatch.setattr(entity, "async_write_ha_state", lambda: writes.append(True))
    entity._handle_event("incoming_call", {"id": 1})
    entity._handle_event("unsupported", {})
    assert calls == [("incoming_call", {"id": 1})] and writes == [True]


def test_voice_bridge_paths(monkeypatch):
    disabled, enabled = [], []
    asyncio.run(
        switch.async_setup_entry(SimpleNamespace(), _entry(quick_voice=False), disabled.extend)
    )
    asyncio.run(switch.async_setup_entry(SimpleNamespace(), _entry(), enabled.extend))
    assert not disabled and len(enabled) == 1
    entity = enabled[0]
    writes = []
    monkeypatch.setattr(entity, "async_write_ha_state", lambda: writes.append(True))
    services = _attach_hass(entity, {"entry-id": {"success": True}})
    assert entity.available
    asyncio.run(entity.async_turn_on())
    asyncio.run(entity.async_turn_off())
    assert services.async_call.await_count == 1 and writes == [True, True]

    failed = switch.BTDoorGateVoiceBridgeSwitch(_entry())
    _attach_hass(failed, {"entry-id": {"success": False, "error": "denied"}})
    with pytest.raises(HomeAssistantError) as exc_info:
        asyncio.run(failed.async_turn_on())
    assert exc_info.value.translation_key == "gate_open_failed"
    assert exc_info.value.translation_placeholders == {"error": "denied"}


def test_gate_and_developer_button_paths(monkeypatch):
    gate = button.BTDoorGateOpenButton(_entry())
    services = _attach_hass(gate, {"entry-id": {"success": True}})
    assert gate.available and gate.extra_state_attributes["quick_voice_assistants_enabled"]
    asyncio.run(gate.async_press())
    assert services.async_call.await_count == 1

    failed = button.BTDoorGateOpenButton(_entry())
    _attach_hass(failed, {"entry-id": {"success": False}})
    with pytest.raises(HomeAssistantError) as exc_info:
        asyncio.run(failed.async_press())
    assert exc_info.value.translation_key == "gate_open_failed"

    developer = SimpleNamespace(
        enabled=True,
        async_run_tests=AsyncMock(return_value={"one": {"ok": True}}),
        async_generate_support_report=AsyncMock(
            return_value={"report_path": "/tmp/r.md", "bundle_path": "/tmp/r.zip"}
        ),
        async_clean_debug_environment=AsyncMock(return_value={"removed_files": 3}),
    )
    notices = []
    monkeypatch.setattr(
        button.persistent_notification, "async_create", lambda *a, **k: notices.append((a, k))
    )
    for cls in (
        button.BTDoorDeveloperTestButton,
        button.BTDoorSupportReportButton,
        button.BTDoorCleanDebugButton,
    ):
        entity = cls(_entry(developer=developer))
        entity.hass = SimpleNamespace()
        monkeypatch.setattr(entity, "async_write_ha_state", lambda: None)
        assert entity.available
        asyncio.run(entity.async_press())
    assert len(notices) == 3


def test_diagnostics_payload(monkeypatch):
    monkeypatch.setattr(diagnostics, "sanitize_support_data", lambda data: data)
    result = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(SimpleNamespace(), _entry())
    )
    assert result["runtime"]["registered"] is True
    assert result["runtime"]["server"] == "sip.example.test"
    assert result["support_debug"]["mode"] == "off"
