"""QS-20 behavioural coverage for setup-entry orchestration and support bundles."""
from __future__ import annotations

import asyncio
import sys
import types
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from test_quality_scale_qs6_developer_lifecycle import _load_developer, _tools
from test_quality_scale_qs8_core_lifecycle_cloud import Config, _install_ha_stubs, _load, _reset_package


@pytest.fixture(autouse=True)
def _restore_modules():
    tracked = {
        name: module
        for name, module in sys.modules.items()
        if name == "custom_components"
        or name.startswith("custom_components.btdoor_security_plus")
        or name.startswith("homeassistant")
    }
    yield
    for name in list(sys.modules):
        if name == "custom_components" or name.startswith("custom_components.btdoor_security_plus") or name.startswith("homeassistant"):
            sys.modules.pop(name, None)
    sys.modules.update(tracked)


def _init_module():
    _reset_package(); _install_ha_stubs(); _load("const")
    return _load("__init__")


@pytest.mark.asyncio
async def test_setup_entry_full_orchestration_and_event_bridge(tmp_path, monkeypatch):
    module = _init_module()
    events: list[object] = []
    listeners: list[object] = []

    class Store:
        def __init__(self, hass, version, key): self.key = key; self.saved = []
        async def async_load(self): return {"registered": True}
        def async_delay_save(self, callback, delay): self.saved.append((callback(), delay))
        async def async_save(self, value): self.saved.append(value)
    module.Store = Store

    class Debug:
        def __init__(self, path, mode): self.path = path; self.mode = mode; self.dropped_records = 0
        async def async_start(self): events.append("debug_start")
        async def async_stop(self): events.append("debug_stop")
        def record(self, *args, **kwargs): events.append((args, kwargs))
    support = types.ModuleType("custom_components.btdoor_security_plus.support_debug")
    support.SupportDebugRecorder = Debug

    class Client:
        def __init__(self):
            self.registered = True; self.last_status = "200 OK"; self.server = "sip.example"; self.port = 5061
        def restore_state(self, state): events.append(("restore", state))
        async def async_start(self): events.append("client_start")
        def add_listener(self, callback): listeners.append(callback); return lambda: events.append("event_unsub")
        def export_state(self): return {"registered": self.registered}
        async def async_stop(self): events.append("client_stop")
    client = Client()
    monkeypatch.setattr(module, "_client_from_entry", lambda entry, debug: client)
    monkeypatch.setattr(module, "_async_migrate_certificate_storage", AsyncMock())
    monkeypatch.setattr(module, "_async_migrate_debug_storage", AsyncMock())
    monkeypatch.setattr(module, "_async_renew_certificate_if_needed", AsyncMock(return_value=False))

    cloud = types.ModuleType("custom_components.btdoor_security_plus.cloud")
    cloud.BticinoCloudAuthenticationError = type("BticinoCloudAuthenticationError", (Exception,), {})
    cloud.BticinoCloudConnectionError = type("BticinoCloudConnectionError", (Exception,), {})
    cloud.BticinoCloudError = type("BticinoCloudError", (Exception,), {})
    developer = types.ModuleType("custom_components.btdoor_security_plus.developer")
    developer.DeveloperModeDisabledError = type("DeveloperModeDisabledError", (Exception,), {})
    developer.DeveloperTools = lambda hass, entry, runtime, enabled: SimpleNamespace(enabled=enabled)
    managers = types.ModuleType("custom_components.btdoor_security_plus.managers")
    managers.async_register_devices = AsyncMock()

    class RuntimeEventType:
        SIP_REGISTERED = "sip_registered"; SIP_UNREGISTERED = "sip_unregistered"
        INTEGRATION_STARTED = "integration_started"; CLOUD_CONNECTED = "cloud_connected"
    class RuntimeSource:
        INTEGRATION = "integration"; SIP = "sip"; CLOUD = "cloud"
    class RuntimeEvent:
        def __init__(self, event_type, source, payload): self.event_type=event_type; self.source=source; self.payload=payload
    class Bus:
        def __init__(self, store): self.store=store; self.published=[]
        async def async_load(self): events.append("bus_load")
        def publish(self, event): self.published.append(event); events.append(("publish", event.event_type))
    event_bus = types.ModuleType("custom_components.btdoor_security_plus.event_bus")
    event_bus.RuntimeEvent = RuntimeEvent; event_bus.RuntimeEventBus = Bus
    event_bus.RuntimeEventType = RuntimeEventType; event_bus.RuntimeSource = RuntimeSource
    event_bus.map_client_event = lambda event_type, data: RuntimeEvent(event_type, "sip", dict(data))

    class Journal:
        def __init__(self, store): self.store=store
        async def async_load(self): events.append("journal_load")
        def attach(self, bus): events.append("journal_attach")
    journal = types.ModuleType("custom_components.btdoor_security_plus.call_journal"); journal.CallJournal = Journal

    class Runtime:
        def __init__(self, **kwargs): self.__dict__.update(kwargs); self.last_open=None; self.last_result=None
    runtime = types.ModuleType("custom_components.btdoor_security_plus.runtime"); runtime.BTDoorRuntimeData = Runtime
    runtime_state = types.ModuleType("custom_components.btdoor_security_plus.runtime_state"); runtime_state.BTDoorRuntimeAPI = lambda entry, data: SimpleNamespace(entry=entry)
    sip = types.ModuleType("custom_components.btdoor_security_plus.sip_client"); sip.BticinoSipError = type("BticinoSipError", (Exception,), {})
    sys.modules.update({m.__name__:m for m in (support, cloud, developer, managers, event_bus, journal, runtime, runtime_state, sip)})

    cert = tmp_path / "cert.pem"; key = tmp_path / "key.pem"; cert.write_text("c"); key.write_text("k")
    fired=[]; updated=[]; scheduled=[]
    class ConfigEntries:
        def async_update_entry(self, *a, **k): updated.append(k)
        async def async_forward_entry_setups(self, entry, platforms): events.append(("forward", tuple(platforms)))
        async def async_reload(self, entry_id): events.append(("reload", entry_id))
    hass = SimpleNamespace(
        config=Config(tmp_path), config_entries=ConfigEntries(),
        bus=SimpleNamespace(async_fire=lambda *a, **k: fired.append((a,k))), entity_registry=SimpleNamespace(),
    )
    module.ir.async_delete_issue=lambda *a, **k: events.append("delete_issue")
    module.async_track_time_interval=lambda hass, callback, interval: scheduled.append(callback) or (lambda: None)
    monkeypatch.setattr(module, "_async_remove_legacy_gate_entities", lambda *a: events.append("legacy_removed"))
    monkeypatch.setattr(module, "_log_availability_transition", lambda *a: events.append(("availability", a[1])))

    entry = SimpleNamespace(
        entry_id="entry", title="Old", unique_id="gw", runtime_data=None,
        data={module.CONF_GATEWAY_ID:"gw", module.CONF_DEVICE_NAME:"Door", module.CONF_CLIENT_CERT_PATH:str(cert), module.CONF_CLIENT_KEY_PATH:str(key)},
        options={module.CONF_DEVELOPER_MODE:True},
        async_on_unload=lambda cb: events.append("on_unload"),
        add_update_listener=lambda cb: cb,
    )
    assert await module.async_setup_entry(hass, entry) is True
    assert entry.title == "Old" and updated[0]["title"] == "Bticino DS+ Suite"
    assert "client_start" in events and "bus_load" in events and "journal_attach" in events
    assert listeners and scheduled and fired == []
    assert any(item == ("publish", RuntimeEventType.SIP_REGISTERED) for item in events)

    listeners[0]("gate_opened", {"status":"ok"})
    assert entry.runtime_data.last_open is not None and entry.runtime_data.last_result == "ok"
    assert fired[-1][0][0] == module.EVENT_BUS
    await scheduled[0](None)


@pytest.mark.asyncio
async def test_generate_support_report_and_event_publication(tmp_path, monkeypatch):
    module = _load_developer(tmp_path)
    tools, client = _tools(module, tmp_path)
    published=[]
    tools.runtime.event_bus = SimpleNamespace(publish=lambda event: published.append(event), history=[], metrics={})
    tools.runtime.call_journal = SimpleNamespace(records=[], metrics={})
    tools.runtime.debug.recent = lambda: []
    tools.hass.states = SimpleNamespace(get=lambda entity_id: SimpleNamespace(state="on"))

    monkeypatch.setattr(tools, "async_run_tests", AsyncMock(return_value={"health":{"ok":True}, "cloud":{"ok":True}, "certificates":{"ok":True}, "tls":{"ok":True}}))
    monkeypatch.setattr(module, "async_get_integration", AsyncMock(return_value=SimpleNamespace(version="1.1.0")))
    monkeypatch.setattr(tools, "_system_info", lambda: {"python":"3.13 test", "platform":"linux"})
    monkeypatch.setattr(tools, "_async_framework_diagnostics", AsyncMock(return_value=({}, {"status":"healthy", "score":100})))
    monkeypatch.setattr(tools, "_entity_registry_report", lambda: {"entities":[]})

    dm = types.ModuleType("custom_components.btdoor_security_plus.device_model.manager")
    dm.device_registry_report=lambda hass, entry: {"devices":[]}
    dm.device_translation_report=lambda entry: {"translations":[]}
    mm = types.ModuleType("custom_components.btdoor_security_plus.managers.device_manager")
    mm.DeviceManager=lambda hass, entry: SimpleNamespace(validate_topology=lambda: SimpleNamespace(as_dict=lambda:{"ok":True}))
    eb = types.ModuleType("custom_components.btdoor_security_plus.event_bus")
    eb.RuntimeEventType=SimpleNamespace(SUPPORT_BUNDLE_CREATED="support_bundle_created")
    eb.RuntimeSource=SimpleNamespace(DIAGNOSTICS="diagnostics")
    eb.RuntimeEvent=lambda **kwargs: SimpleNamespace(**kwargs)
    sys.modules.update({dm.__name__:dm, mm.__name__:mm, eb.__name__:eb})

    result = await tools.async_generate_support_report(include_logs=False)
    assert Path(result["report_path"]).is_file() and Path(result["bundle_path"]).is_file()
    with zipfile.ZipFile(result["bundle_path"]) as archive:
        assert "support_summary.json" in archive.namelist()
        assert not any(name.startswith("logs/") for name in archive.namelist())
    assert tools.runtime.last_support_report_path == result["report_path"]
    assert published and published[0].event_type == "support_bundle_created"


def _sip_module():
    _reset_package(); _load("const"); _load("sip_identity"); _load("media")
    return _load("sip_client")


def test_sip_sdp_and_digest_residual_branches(monkeypatch):
    sip = _sip_module()
    sdp = """v=0
s=Door Call
c=IN IP4 192.0.2.1
a=sendonly
m=audio bad RTP/SAVP 0 x 96
a=rtpmap:x invalid
a=rtpmap:96 opus/48000/2
a=fmtp:x broken
a=fmtp:96 useinbandfec=1
a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2
m=video 5000 RTP/AVP 96 34
a=recvonly
a=rtpmap:96 H264/90000
a=rtcp-fb:96 nack pli
a=rtcp-fb:* trr-int 100
a=fmtp:96 profile-level-id=42e01f
c=IN IP4 192.0.2.2
"""
    description = sip.BticinoSipClient._parse_sdp(sdp)
    assert description.session_name == "Door Call"
    assert len(description.media) == 2
    assert description.media[0].port == 0
    assert description.media[1].connection_address == "192.0.2.2"
    assert description.media[1].rtcp_feedback[96] == ("nack pli",)

    client = sip.BticinoSipClient(
        sip_account="sip:user@example.com", sip_password="secret", gateway_id="gw",
        client_cert_path="cert", client_key_path="key", server="sip.example", port=5061, verify_server=True,
    )
    prep = SimpleNamespace(
        state="prepared", issues=(), answer_sdp_redacted="v=0", srtp_suite="AES",
        audio_codec="PCMU", video_codec="H264", answer_sdp_fingerprint="fp",
        local_media_address="192.0.2.10", public_dict=lambda: {"state":"prepared"},
    )
    monkeypatch.setattr(sip, "prepare_media_offer", lambda description: prep)
    monkeypatch.setattr(sip, "media_snapshot", lambda preparation: {"state": preparation.state})
    monkeypatch.setattr(sip, "build_sdp_diff", lambda remote, local: "diff")
    client.last_sdp_offer = sdp
    client._apply_sdp(description)
    assert client.sdp_audio_port == 0 and client.sdp_video_port == 5000
    assert "video" in client.last_sdp_summary

    challenge = 'Digest realm="realm", nonce="nonce", algorithm=MD5-sess, qop="auth,auth-int", opaque="opaque"'
    auth = client._make_digest_auth(challenge, "REGISTER", "sip:example.com", "user", "secret")
    assert "algorithm=MD5-SESS" in auth and 'opaque="opaque"' in auth and "qop=auth" in auth
    no_qop = client._make_digest_auth('Digest realm="r", nonce="n"', "OPTIONS", "sip:x", "u", "p")
    assert "qop=" not in no_qop
    with pytest.raises(sip.BticinoSipAuthenticationError, match="Unsupported Digest algorithm"):
        client._make_digest_auth('Digest realm="r", nonce="n", algorithm=SHA-256', "REGISTER", "sip:x", "u", "p")
    with pytest.raises(sip.BticinoSipAuthenticationError, match="challenge missing"):
        client._challenge({})
    assert client._challenge({"www-authenticate":["x"]}) == ("x", "Authorization")
    assert client._challenge({"proxy-authenticate":["y"]}) == ("y", "Proxy-Authorization")
    with pytest.raises(sip.BticinoSipConnectionError, match="Invalid or stale"):
        client._status_code("not a response")

@pytest.mark.asyncio
async def test_public_package_exports_and_lazy_device_registration(monkeypatch):
    import importlib
    _reset_package()
    ha = types.ModuleType("homeassistant")
    helpers = types.ModuleType("homeassistant.helpers")
    device_registry = types.ModuleType("homeassistant.helpers.device_registry")
    device_registry.DeviceInfo = dict
    sys.modules.update({ha.__name__: ha, helpers.__name__: helpers, device_registry.__name__: device_registry})

    adapters = importlib.import_module("custom_components.btdoor_security_plus.adapters")
    analysis = importlib.import_module("custom_components.btdoor_security_plus.analysis")
    assert adapters.DeviceAdapter and analysis.RuntimeSummary

    device_model = importlib.import_module("custom_components.btdoor_security_plus.device_model")
    manager = types.ModuleType("custom_components.btdoor_security_plus.device_model.manager")
    register = AsyncMock()
    manager.async_register_devices = register
    monkeypatch.setitem(sys.modules, manager.__name__, manager)
    await device_model.async_register_devices("hass", "entry")
    register.assert_awaited_once_with("hass", "entry")
