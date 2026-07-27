"""QS-3 behavioural coverage for the large sensor platform."""
from __future__ import annotations

import asyncio
import importlib.util
import inspect
import sys
import types
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "custom_components" / "btdoor_security_plus"


class _Entity:
    def async_on_remove(self, callback):
        self._remove_callback = callback

    async def async_added_to_hass(self):
        return None

    def async_write_ha_state(self):
        self._written = True


class _SensorEntity(_Entity):
    pass


def _load(name: str):
    full_name = f"custom_components.btdoor_security_plus.{name.replace('/', '.')}"
    file_path = PKG_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _install_stubs():
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus"):
            sys.modules.pop(name)
    root_pkg = types.ModuleType("custom_components")
    root_pkg.__path__ = [str(ROOT / "custom_components")]
    sys.modules["custom_components"] = root_pkg
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG_DIR)]
    package.BticinoConfigEntry = object
    sys.modules[package.__name__] = package

    ha = types.ModuleType("homeassistant")
    components = types.ModuleType("homeassistant.components")
    helpers = types.ModuleType("homeassistant.helpers")
    sys.modules.update({"homeassistant": ha, "homeassistant.components": components, "homeassistant.helpers": helpers})

    sensor_mod = types.ModuleType("homeassistant.components.sensor")
    sensor_mod.SensorEntity = _SensorEntity
    sensor_mod.SensorDeviceClass = SimpleNamespace(TIMESTAMP="timestamp")
    sys.modules[sensor_mod.__name__] = sensor_mod
    components.sensor = sensor_mod

    const_mod = types.ModuleType("homeassistant.const")
    const_mod.EntityCategory = SimpleNamespace(DIAGNOSTIC="diagnostic")
    const_mod.UnitOfTime = SimpleNamespace(SECONDS="s")
    sys.modules[const_mod.__name__] = const_mod

    core_mod = types.ModuleType("homeassistant.core")
    core_mod.HomeAssistant = object
    sys.modules[core_mod.__name__] = core_mod

    ep_mod = types.ModuleType("homeassistant.helpers.entity_platform")
    ep_mod.AddConfigEntryEntitiesCallback = object
    sys.modules[ep_mod.__name__] = ep_mod

    entity_mod = types.ModuleType("homeassistant.helpers.entity")
    entity_mod.Entity = _Entity
    sys.modules[entity_mod.__name__] = entity_mod

    dr_mod = types.ModuleType("homeassistant.helpers.device_registry")
    dr_mod.DeviceInfo = dict
    sys.modules[dr_mod.__name__] = dr_mod


_install_stubs()
factory = _load("device_model/factory")
model_pkg = types.ModuleType("custom_components.btdoor_security_plus.device_model")
model_pkg.__path__ = [str(PKG_DIR / "device_model")]
model_pkg.DeviceKind = factory.DeviceKind
model_pkg.device_info_for = factory.device_info_for
sys.modules[model_pkg.__name__] = model_pkg
visibility_manager = _load("visibility/manager")
visibility_pkg = types.ModuleType("custom_components.btdoor_security_plus.visibility")
visibility_pkg.__path__ = [str(PKG_DIR / "visibility")]
visibility_pkg.visibility_for_entry = visibility_manager.visibility_for_entry
sys.modules[visibility_pkg.__name__] = visibility_pkg
_load("entity")
_load("entity_metrics")
analysis_pkg = types.ModuleType("custom_components.btdoor_security_plus.analysis")
analysis_pkg.__path__ = [str(PKG_DIR / "analysis")]
sys.modules[analysis_pkg.__name__] = analysis_pkg
runtime_summary = _load("analysis/runtime_summary")
analysis_pkg.RuntimeSummary = runtime_summary.RuntimeSummary
analysis_pkg.build_runtime_summary = runtime_summary.build_runtime_summary
sensor = _load("sensor")


def _snapshot():
    value = SimpleNamespace(
        diagnostics=SimpleNamespace(status="healthy", score=98, issues=()),
        gateway=SimpleNamespace(gateway_name="Front gate", device_name="Door"),
        cloud=SimpleNamespace(connected=True, status="connected"),
        sip=SimpleNamespace(registered=True, status="200 OK"),
        dialog=SimpleNamespace(state="idle", call_state="idle", caller="Visitor"),
        media=SimpleNamespace(
            state="ready", ready=True, audio_codec="PCMU", video_codec="H264",
            srtp_suite="AES_CM_128_HMAC_SHA1_80", duration_seconds=4.2,
            close_reason="bye",
        ),
    )
    value.as_dict = lambda: {"gateway": {}, "cloud": {}, "sip": {}, "dialog": {}, "media": {}, "diagnostics": {}}
    return value


def _entry(*, developer=True, api=True):
    now = datetime.now(UTC)
    client = SimpleNamespace(
        registered=True, last_status="200 OK", last_open=now, last_event_type="incoming_call",
        last_caller="Visitor", last_caller_uri="sip:visitor@example", last_caller_domain="example",
        last_caller_tag="tag", last_caller_display_name="Visitor", last_caller_raw="raw",
        last_call_id="call-1", call_state="idle", last_sip_method="INVITE",
        last_message="hello", last_call_duration=1.234, call_count=3,
        call_started_at=now-timedelta(seconds=2), call_ended_at=now,
        missed_call_count=1, message_count=2, last_message_at=now,
        last_event_at=now, reconnect_count=1, last_error=None,
        connected_at=now-timedelta(seconds=10), last_command_duration=0.5,
        last_command_at=now, dialog_state="idle", last_sdp_offer="v=0\n"*100,
        last_sdp_summary="audio+video", sdp_audio_port=4000, sdp_audio_address="10.0.0.2",
        sdp_audio_direction="sendrecv", sdp_audio_codecs=("PCMU",),
        sdp_video_port=5000, sdp_video_address="10.0.0.2", sdp_video_direction="sendrecv",
        sdp_video_codecs=("H264",), media_runtime_state="prepared",
        media_runtime={"state":"prepared"}, media_plan={
            "audio":{"codec":"PCMU"}, "video":{"codec":"H264"},
            "srtp":{"suite":"AES_CM_128_HMAC_SHA1_80"}},
        media_session_metrics={"retained_sessions":2},
        last_completed_media_session={"closed_reason":"bye", "call_id":"call-1", "duration_seconds":4.2},
        add_listener=lambda callback: lambda: None,
    )
    cloud = SimpleNamespace(
        status="connected", connected=True, authenticated=True, certificate_ready=True,
        last_request="req", last_response="resp", endpoint="https://api.example", last_error=None,
    )
    dialog = SimpleNamespace(state="idle", call_id="call-1", caller="Visitor", started_at=now, ended_at=now)
    media = SimpleNamespace(close_reason="bye", retained_sessions=2, duration_seconds=4.2, audio_codec="PCMU", video_codec="H264", started_at=now, closed_at=now)
    diagnostics = SimpleNamespace(
        status="healthy", score=98, sip_registered=True, dialog_state="idle",
        media_state="ready", last_error=None, issues=(),
    )
    api_obj = SimpleNamespace(
        snapshot=_snapshot, cloud=lambda: cloud, dialog=lambda: dialog,
        media=lambda: media, diagnostics=lambda: diagnostics,
    ) if api else None
    event_bus = SimpleNamespace(
        subscribe=lambda callback: lambda: None,
        history=[{"event_type":"incoming_call"}],
        metrics={"total_events":1, "events_by_type":{"incoming_call":1}},
        last_event=SimpleNamespace(event_type="incoming_call", timestamp=now, payload={"id":1}),
        last_event_summary={"event_type":"incoming_call", "timestamp":now.isoformat()},
        retained_count=1, compact_history=lambda limit: [{"event_type":"incoming_call"}],
    )
    journal = SimpleNamespace(
        last_record={"result":"answered", "caller":"Visitor"}, records=[1,2],
        metrics={"calls_by_result":{"missed":1}, "average_duration_seconds":3.5,
                 "answered_today":1, "missed_today":1},
    )
    runtime = SimpleNamespace(
        client=client, api=api_obj, last_open=now,
        last_developer_test_result="passed", last_developer_test_at=now,
        last_support_report_at=now, last_support_report_path="/tmp/report.json",
        last_support_bundle_path="/tmp/bundle.zip", event_bus=event_bus,
        call_journal=journal,
    )
    return SimpleNamespace(
        unique_id="uid", entry_id="entry", data={"gateway_id":"gw", "gateway_name":"Front"},
        options={"developer_mode": developer}, runtime_data=runtime,
    )


def _sensor_classes():
    for _, cls in inspect.getmembers(sensor, inspect.isclass):
        if cls.__module__ == sensor.__name__ and cls.__name__.startswith(("Bticino", "BTDoor")):
            yield cls


def test_sensor_setup_filters_and_developer_mode(monkeypatch):
    added = []
    monkeypatch.setattr(sensor, "visibility_for_entry", lambda _: SimpleNamespace(filter_entities=lambda values: values))
    asyncio.run(sensor.async_setup_entry(SimpleNamespace(), _entry(developer=False), added.extend))
    assert len(added) == 43
    added.clear()
    asyncio.run(sensor.async_setup_entry(SimpleNamespace(), _entry(developer=True), added.extend))
    assert len(added) == 51


def test_all_sensor_values_attributes_and_listener_paths():
    entry = _entry()
    entities = [cls(entry) for cls in _sensor_classes()]
    assert len(entities) >= 50
    for entity in entities:
        if hasattr(type(entity), "native_value"):
            _ = entity.native_value
        if hasattr(type(entity), "extra_state_attributes"):
            _ = entity.extra_state_attributes
        if hasattr(entity, "async_added_to_hass"):
            asyncio.run(entity.async_added_to_hass())
    assert all(getattr(entity, "_attr_unique_id", "").startswith("uid_") for entity in entities)


def test_sensor_branch_variants():
    entry = _entry(api=False)
    client = entry.runtime_data.client
    quality = sensor.BticinoConnectionQualitySensor(entry)
    client.registered = False; assert quality.native_value == "offline"
    client.registered = True; client.last_error = "x"; assert quality.native_value == "poor"
    client.last_error = None
    for duration, expected in ((None,"good"),(0.5,"excellent"),(1.0,"good"),(2.0,"average"),(4.0,"poor")):
        client.last_command_duration = duration; assert quality.native_value == expected
    client.sdp_audio_port = None; assert sensor.BticinoAudioOfferSensor(entry).native_value is None
    client.sdp_video_port = None; assert sensor.BticinoVideoOfferSensor(entry).native_value is None
    client.last_sdp_offer = None; assert sensor.BticinoLastSdpOfferSensor(entry).native_value is None
    client.last_call_duration = None; assert sensor.BticinoLastCallDurationSensor(entry).native_value is None
    client.connected_at = None; assert sensor.BticinoConnectionUptimeSensor(entry).native_value is None
    client.media_plan = None
    assert sensor.BticinoSelectedAudioCodecSensor(entry).native_value is None
    assert sensor.BticinoSelectedVideoCodecSensor(entry).extra_state_attributes == {}
    assert sensor.BticinoSrtpSuiteSensor(entry).native_value is None
    assert sensor.BTDoorRuntimeHealthSensor(entry).native_value == "healthy"
    assert sensor.BTDoorRuntimeScoreSensor(entry).native_value == 100
    entry.runtime_data.call_journal = None
    assert sensor.BTDoorCallJournalCountSensor(entry).native_value == 0
    assert sensor.BTDoorCallJournalAverageDurationSensor(entry).native_value is None


def test_developer_runtime_inspector_states():
    entry = _entry()
    entity = sensor.BTDoorDeveloperRuntimeInspectorSensor(entry)
    assert entity.native_value == "healthy"
    entry.runtime_data.api = None
    assert entity.native_value == "unavailable"
