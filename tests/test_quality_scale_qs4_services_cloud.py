"""QS-4 behavioural coverage for services and cloud helpers."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


class HomeAssistantError(Exception):
    def __init__(self, message=None, *, translation_domain=None, translation_key=None, translation_placeholders=None):
        self.translation_domain = translation_domain
        self.translation_key = translation_key
        self.translation_placeholders = translation_placeholders or {}
        rendered = message or self.translation_placeholders.get("error") or translation_key or ""
        super().__init__(rendered)


class ServiceValidationError(HomeAssistantError):
    pass


class _SupportsResponse:
    OPTIONAL = "optional"
    NONE = "none"


class _Services:
    def __init__(self):
        self.handlers = {}
        self.removed = []

    def has_service(self, domain, name):
        return (domain, name) in self.handlers

    def async_register(self, domain, name, handler, **kwargs):
        self.handlers[(domain, name)] = (handler, kwargs)

    def async_remove(self, domain, name):
        self.removed.append((domain, name))
        self.handlers.pop((domain, name), None)


class _Bus:
    def __init__(self):
        self.events = []

    def async_fire(self, event, data, context=None):
        self.events.append((event, data, context))


class _ConfigEntries:
    def __init__(self, entries):
        self.entries = entries

    def async_entries(self, domain):
        return self.entries


class _Hass:
    def __init__(self, entries, tmp_path):
        self.services = _Services()
        self.bus = _Bus()
        self.config_entries = _ConfigEntries(entries)
        self.config = SimpleNamespace(path=lambda *parts: str(tmp_path.joinpath(*parts)))

    async def async_add_executor_job(self, target, *args):
        return target(*args)


def _load(name: str):
    full = f"custom_components.btdoor_security_plus.{name}"
    spec = importlib.util.spec_from_file_location(full, PKG / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def _install_services_stubs():
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus") or name.startswith("homeassistant"):
            sys.modules.pop(name, None)
    root = types.ModuleType("custom_components")
    root.__path__ = [str(ROOT / "custom_components")]
    sys.modules[root.__name__] = root
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG)]
    sys.modules[package.__name__] = package

    vol = types.ModuleType("voluptuous")
    vol.Schema = lambda value: value
    vol.Optional = lambda key, default=None: key
    vol.Any = lambda *values: values[0]
    vol.In = lambda values: lambda value: value
    sys.modules["voluptuous"] = vol

    ha = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    core.ServiceCall = object
    core.SupportsResponse = _SupportsResponse
    exc = types.ModuleType("homeassistant.exceptions")
    exc.HomeAssistantError = HomeAssistantError
    exc.ServiceValidationError = ServiceValidationError
    helpers = types.ModuleType("homeassistant.helpers")
    cv = types.ModuleType("homeassistant.helpers.config_validation")
    cv.string = str
    cv.entity_id = str
    cv.boolean = bool
    er = types.ModuleType("homeassistant.helpers.entity_registry")
    er.async_get = lambda hass: hass.entity_registry
    helpers.config_validation = cv
    helpers.entity_registry = er
    sys.modules.update({
        "homeassistant": ha,
        "homeassistant.core": core,
        "homeassistant.exceptions": exc,
        "homeassistant.helpers": helpers,
        cv.__name__: cv,
        er.__name__: er,
    })


@pytest.fixture
def services_module():
    _install_services_stubs()
    const = _load("const")
    developer = types.ModuleType("custom_components.btdoor_security_plus.developer")
    class DeveloperModeDisabledError(Exception):
        pass
    developer.DeveloperModeDisabledError = DeveloperModeDisabledError
    sys.modules[developer.__name__] = developer
    event_bus = types.ModuleType("custom_components.btdoor_security_plus.event_bus")
    event_bus.RuntimeEvent = SimpleNamespace(from_dict=lambda item: SimpleNamespace(**item))
    sys.modules[event_bus.__name__] = event_bus
    sip = types.ModuleType("custom_components.btdoor_security_plus.sip_client")
    class BticinoSipError(Exception):
        pass
    sip.BticinoSipError = BticinoSipError
    sys.modules[sip.__name__] = sip
    return _load("services"), const, DeveloperModeDisabledError, BticinoSipError


def _entry(entry_id="entry-1"):
    debug = SimpleNamespace(record=lambda *args, **kwargs: None)
    client = SimpleNamespace(
        async_open_gate=AsyncMock(return_value=SimpleNamespace(status="opened", code=200)),
        reset_statistics=lambda: None,
        export_state=lambda: {"ok": True},
        async_test_connection=AsyncMock(),
        async_reject_call=AsyncMock(),
    )
    runtime = SimpleNamespace(
        client=client,
        debug=debug,
        last_result=None,
        last_open=None,
        store=SimpleNamespace(async_save=AsyncMock()),
        developer=SimpleNamespace(
            async_run_tests=AsyncMock(return_value={"status": "ok"}),
            async_generate_support_report=AsyncMock(return_value={"path": "report"}),
            async_clean_debug_environment=AsyncMock(return_value={"clean": True}),
        ),
        call_journal=SimpleNamespace(
            async_clear=AsyncMock(), export_state=lambda: {"calls": []},
            async_rebuild=AsyncMock(), metrics={"total": 1},
        ),
        event_bus=SimpleNamespace(history=[{"event_type": "incoming_call", "payload": {}}]),
    )
    return SimpleNamespace(entry_id=entry_id, data={"gateway_id": "gw-1"}, runtime_data=runtime)


@pytest.mark.asyncio
async def test_services_selection_registration_and_handlers(tmp_path, services_module):
    services, const, _, _ = services_module
    first, second = _entry(), _entry("entry-2")
    hass = _Hass([first, second], tmp_path)
    hass.entity_registry = SimpleNamespace(async_get=lambda entity_id: SimpleNamespace(config_entry_id="entry-2") if entity_id == "button.gate" else None)

    with pytest.raises(HomeAssistantError):
        services._service_entries(hass, SimpleNamespace(data={}), require_single=True)
    assert services._service_entries(hass, SimpleNamespace(data={"entry_id": "entry-1"}))[0] is first
    assert services._service_entries(hass, SimpleNamespace(data={"entity_id": "button.gate"}))[0] is second
    with pytest.raises(HomeAssistantError):
        services._service_entries(hass, SimpleNamespace(data={"entry_id": "missing"}))

    await services.async_register_services(hass)
    assert len(hass.services.handlers) == len(services.REGISTERED_SERVICES)
    await services.async_register_services(hass)  # idempotent

    def call(data=None):
        return SimpleNamespace(data=data or {}, context=SimpleNamespace(user_id="user"))

    open_handler = hass.services.handlers[(const.DOMAIN, const.SERVICE_OPEN_GATE)][0]
    result = await open_handler(call({"entry_id": "entry-1", "reason": "test", "source": "pytest"}))
    assert result["entry-1"]["success"] is True
    assert first.runtime_data.last_result == "opened"
    assert hass.bus.events[-1][1]["event_type"] == "gate_open_succeeded"

    await hass.services.handlers[(const.DOMAIN, const.SERVICE_RESET_STATISTICS)][0](call({"entry_id": "entry-1"}))
    first.runtime_data.store.async_save.assert_awaited_once_with({"ok": True})
    await hass.services.handlers[(const.DOMAIN, const.SERVICE_TEST_CONNECTION)][0](call({"entry_id": "entry-1"}))
    await hass.services.handlers[(const.DOMAIN, const.SERVICE_REJECT_CALL)][0](call({"entry_id": "entry-1"}))
    assert (await hass.services.handlers[(const.DOMAIN, const.SERVICE_DEVELOPER_TEST)][0](call({"entry_id": "entry-1", "test": "sip"})))["entry-1"] == {"status": "ok"}
    assert (await hass.services.handlers[(const.DOMAIN, const.SERVICE_GENERATE_SUPPORT_REPORT)][0](call({"entry_id": "entry-1", "include_logs": False})))["entry-1"] == {"path": "report"}
    assert (await hass.services.handlers[(const.DOMAIN, const.SERVICE_CLEAN_DEBUG_ENVIRONMENT)][0](call({"entry_id": "entry-1"})))["entry-1"] == {"clean": True}
    assert (await hass.services.handlers[(const.DOMAIN, const.SERVICE_CLEAR_CALL_JOURNAL)][0](call({"entry_id": "entry-1"})))["entry-1"] == {"cleared": True}
    export = await hass.services.handlers[(const.DOMAIN, const.SERVICE_EXPORT_CALL_JOURNAL)][0](call({"entry_id": "entry-1"}))
    exported = Path(export["entry-1"]["path"])
    assert exported.exists() and json.loads(exported.read_text())["calls"] == []
    rebuilt = await hass.services.handlers[(const.DOMAIN, const.SERVICE_REBUILD_CALL_JOURNAL)][0](call({"entry_id": "entry-1"}))
    assert rebuilt["entry-1"] == {"total": 1}

    services.async_unregister_services(hass)
    assert len(hass.services.removed) == len(services.REGISTERED_SERVICES)


@pytest.mark.asyncio
async def test_services_error_paths(tmp_path, services_module, monkeypatch):
    services, const, DeveloperModeDisabledError, BticinoSipError = services_module
    entry = _entry()
    hass = _Hass([entry], tmp_path)
    hass.entity_registry = SimpleNamespace(async_get=lambda entity_id: None)
    await services.async_register_services(hass)
    call = lambda data=None: SimpleNamespace(data=data or {"entry_id": "entry-1"}, context=None)

    entry.runtime_data.client.async_open_gate = AsyncMock(side_effect=BticinoSipError("offline"))
    result = await hass.services.handlers[(const.DOMAIN, const.SERVICE_OPEN_GATE)][0](call())
    assert result["entry-1"]["success"] is False and result["entry-1"]["status"] == "error"

    entry.runtime_data.client.async_test_connection = AsyncMock(side_effect=BticinoSipError("bad"))
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.handlers[(const.DOMAIN, const.SERVICE_TEST_CONNECTION)][0](call())
    assert exc_info.value.translation_key == "sip_connection_test_failed"
    assert exc_info.value.translation_placeholders == {"error": "bad"}
    entry.runtime_data.client.async_reject_call = AsyncMock(side_effect=BticinoSipError("bad"))
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.handlers[(const.DOMAIN, const.SERVICE_REJECT_CALL)][0](call())
    assert exc_info.value.translation_key == "call_rejection_failed"
    entry.runtime_data.developer.async_run_tests = AsyncMock(side_effect=DeveloperModeDisabledError("disabled"))
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.handlers[(const.DOMAIN, const.SERVICE_DEVELOPER_TEST)][0](call())
    assert exc_info.value.translation_key == "developer_mode_disabled"
    entry.runtime_data.developer.async_generate_support_report = AsyncMock(side_effect=DeveloperModeDisabledError("disabled"))
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.handlers[(const.DOMAIN, const.SERVICE_GENERATE_SUPPORT_REPORT)][0](call())
    assert exc_info.value.translation_key == "developer_mode_disabled"


def _load_cloud():
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus"):
            sys.modules.pop(name, None)
    root = types.ModuleType("custom_components")
    root.__path__ = [str(ROOT / "custom_components")]
    sys.modules[root.__name__] = root
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG)]
    sys.modules[package.__name__] = package
    return _load("cloud")


def test_cloud_parsing_and_identity_helpers(tmp_path):
    cloud = _load_cloud()
    assert cloud._looks_like_auth_rejection(401, "", {})
    assert cloud._looks_like_auth_rejection(500, "", {})
    assert cloud._looks_like_auth_rejection(200, "login failed", {})
    assert not cloud._looks_like_auth_rejection(429, "rate limited", {})

    gateway = cloud.PlantGateway("p", "Home", "gw", "Front")
    assert gateway.label == "Home - Front (gw)"
    assert cloud.PlantGateway("p", "", "gw", "").label == "BTDoor Security+ - gw (gw)"
    assert len(cloud.generate_id_device()) == 12

    assert cloud._parse_payload({"payload": json.dumps(json.dumps({"x": 1}))}) == {"x": 1}
    assert cloud._items({"Plants": [{"id": 1}]}) == [{"id": 1}]
    assert cloud._items([json.dumps({"id": 2}), "bad", 3]) == [{"id": 2}]
    assert cloud._get({"GatewayId": "abc"}, "gatewayid") == "abc"
    assert cloud._decode_certificate_response(b"plain") == b"plain"

    key = tmp_path / "key.pem"; cert = tmp_path / "cert.pem"; full = tmp_path / "full.pem"; chain = tmp_path / "chain.pem"
    cloud._write_certificate_files(key, cert, full, chain, b"KEY", b"CERT", b"CHAIN")
    assert key.read_bytes() == b"KEY" and full.read_bytes() == b"CERTCHAIN"
    cloud._write_certificate_files(key, cert, full, chain, b"KEY2", b"CERT2", None)
    assert not chain.exists() and (tmp_path / "backup").exists()
    assert cloud.certificate_expiry(tmp_path / "missing.pem") is None


@pytest.mark.asyncio
async def test_cloud_client_login_gateways_and_sip_reuse(tmp_path):
    cloud = _load_cloud()
    client = cloud.BticinoCloudClient(SimpleNamespace(), email=" user@example.com ", password="pw", base_url="https://x/")
    assert client.email == "user@example.com" and client.base_url == "https://x"

    client._request = AsyncMock(return_value=({"auth_token": "token"}, {}))
    await client.async_login()
    assert client.auth_token == "token"
    client.auth_token = ""
    client._request = AsyncMock(return_value=({}, {}))
    with pytest.raises(cloud.BticinoCloudAuthenticationError):
        await client.async_login()

    client.auth_token = "token"
    client._request = AsyncMock(side_effect=[
        ({"plants": [{"PlantId": "p1", "PlantName": "Home"}, {"Name": "skip"}]}, {}),
        ({"gateways": [{"GatewayId": "g1", "Name": "Front"}, {"Name": "skip"}]}, {}),
    ])
    gateways = await client.async_list_gateways()
    assert gateways == [cloud.PlantGateway("p1", "Home", "g1", "Front")]

    selection = gateways[0]
    client._request = AsyncMock(return_value=({"users": [{"SipAccount": "user-example.com-id@g1.bs.iotleg.com", "SipPassword": "pw", "IdDevice": "id"}]}, {}))
    user = await client._async_get_or_create_sip_user(selection=selection, device_name="HA", id_device="id")
    assert user["SipPassword"] == "pw"

    client._request = AsyncMock(side_effect=[({"users": []}, {}), ({"users": [{"SipAccount": "new", "SipPassword": "pw"}]}, {}), ({"users": [{"SipAccount": "user-example.com-id@g1.bs.iotleg.com", "SipPassword": "pw"}]}, {})])
    created = await client._async_get_or_create_sip_user(selection=selection, device_name="HA", id_device="id")
    assert created["SipPassword"] == "pw"
