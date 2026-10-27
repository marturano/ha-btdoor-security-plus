"""Behavioural coverage for every BTDoor Security+ config-flow outcome.

The repository test environment intentionally does not install Home Assistant.  This
module supplies a minimal contract-compatible harness and executes the integration's
real config_flow.py implementation.  It validates outcomes, error mapping, duplicate
prevention, gateway selection, reauthentication, reconfiguration, and options safety.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"


class _Marker:
    def __init__(self, key, default=None):
        self.key = key
        self.default = default

    def __hash__(self):
        return hash(self.key)


class _Schema:
    def __init__(self, schema):
        self.schema = schema


class _Selector:
    def __init__(self, config=None):
        self.config = config


class _FlowBase:
    VERSION = 1

    def __init_subclass__(cls, **kwargs):
        kwargs.pop("domain", None)
        return super().__init_subclass__()

    def __init__(self):
        self.hass = types.SimpleNamespace(
            config=types.SimpleNamespace(path=lambda *parts: "/tmp/" + "/".join(parts))
        )
        self.context = {}
        self._configured_unique_ids: set[str] = set()
        self._unique_id = None
        self._reauth_entry = None
        self._reconfigure_entry_for_test = None

    def async_show_form(self, *, step_id, data_schema=None, errors=None):
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
        }

    def async_create_entry(self, *, title, data):
        return {"type": "create_entry", "title": title, "data": data}

    async def async_set_unique_id(self, unique_id):
        self._unique_id = unique_id

    def _abort_if_unique_id_configured(self):
        if self._unique_id in self._configured_unique_ids:
            return self.async_abort(reason="already_configured")

    def _abort_if_unique_id_mismatch(self, *, reason):
        entry = self._reconfigure_entry_for_test
        if entry and self._unique_id != entry.unique_id:
            raise RuntimeError(reason)

    def async_abort(self, *, reason):
        return {"type": "abort", "reason": reason}

    def async_update_and_abort(self, entry, *, title, data_updates):
        return {
            "type": "abort",
            "reason": "reconfigure_successful",
            "entry": entry,
            "title": title,
            "data_updates": data_updates,
        }

    def _get_reauth_entry(self):
        return self._reauth_entry

    def _get_reconfigure_entry(self):
        return self._reconfigure_entry_for_test


class _OptionsFlow(_FlowBase):
    def __init__(self):
        super().__init__()
        self.config_entry = types.SimpleNamespace(options={})


@dataclass(slots=True)
class _Gateway:
    plant_id: str = "plant-1"
    plant_name: str = "Home"
    gateway_id: str = "gw-1"
    gateway_name: str = "Door"

    @property
    def label(self):
        return f"{self.plant_name} - {self.gateway_name} ({self.gateway_id})"


class CloudError(Exception):
    pass


class CloudAuthError(CloudError):
    pass


class CloudConnectionError(CloudError):
    pass


class SipError(Exception):
    pass


class SipAuthError(SipError):
    pass


class SipConnectionError(SipError):
    pass


def _install_stubs(monkeypatch):
    vol = types.ModuleType("voluptuous")
    vol.Schema = _Schema
    vol.Required = lambda key, default=None: _Marker(key, default)
    vol.Optional = lambda key, default=None: _Marker(key, default)
    monkeypatch.setitem(sys.modules, "voluptuous", vol)

    ha = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    config_entries.ConfigFlow = _FlowBase
    config_entries.OptionsFlow = _OptionsFlow
    config_entries.ConfigFlowResult = dict
    helpers = types.ModuleType("homeassistant.helpers")
    aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
    aiohttp_client.async_get_clientsession = lambda hass: object()
    selector = types.ModuleType("homeassistant.helpers.selector")
    selector.BooleanSelector = _Selector
    selector.SelectSelector = _Selector
    selector.TextSelector = _Selector
    selector.SelectSelectorConfig = lambda **kwargs: kwargs
    selector.TextSelectorConfig = lambda **kwargs: kwargs
    selector.SelectSelectorMode = types.SimpleNamespace(DROPDOWN="dropdown")
    selector.TextSelectorType = types.SimpleNamespace(
        EMAIL="email", PASSWORD="password", TEXT="text"
    )
    monkeypatch.setitem(sys.modules, "homeassistant", ha)
    monkeypatch.setitem(sys.modules, "homeassistant.config_entries", config_entries)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers", helpers)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.aiohttp_client", aiohttp_client)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.selector", selector)

    pkg = types.ModuleType("custom_components.btdoor_security_plus")
    pkg.__path__ = [str(COMPONENT)]
    monkeypatch.setitem(sys.modules, "custom_components", types.ModuleType("custom_components"))
    monkeypatch.setitem(sys.modules, "custom_components.btdoor_security_plus", pkg)

    cloud = types.ModuleType("custom_components.btdoor_security_plus.cloud")
    cloud.BticinoCloudAuthenticationError = CloudAuthError
    cloud.BticinoCloudConnectionError = CloudConnectionError
    cloud.BticinoCloudError = CloudError
    cloud.BticinoCloudClient = object
    cloud.PlantGateway = _Gateway
    cloud.generate_id_device = lambda: "generated-device"
    monkeypatch.setitem(sys.modules, cloud.__name__, cloud)

    sip = types.ModuleType("custom_components.btdoor_security_plus.sip_client")
    sip.BticinoSipAuthenticationError = SipAuthError
    sip.BticinoSipConnectionError = SipConnectionError
    sip.BticinoSipError = SipError
    sip.BticinoSipClient = object
    monkeypatch.setitem(sys.modules, sip.__name__, sip)

    const = types.ModuleType("custom_components.btdoor_security_plus.const")
    values = {
        "CONF_CA_CHAIN_PATH": "ca_chain_path",
        "CONF_CERTIFICATE_NOT_AFTER": "certificate_not_after",
        "CONF_CLIENT_CERT_PATH": "client_cert_path",
        "CONF_CLIENT_KEY_PATH": "client_key_path",
        "CONF_DEVICE_NAME": "device_name",
        "CONF_EMAIL": "email",
        "CONF_GATEWAY_ID": "gateway_id",
        "CONF_GATEWAY_NAME": "gateway_name",
        "CONF_ID_DEVICE": "id_device",
        "CONF_PASSWORD": "password",
        "CONF_PLANT_ID": "plant_id",
        "CONF_PLANT_NAME": "plant_name",
        "CONF_PORT": "port",
        "CONF_SERVER": "server",
        "CONF_SIP_ACCOUNT": "sip_account",
        "CONF_SIP_PASSWORD": "sip_password",
        "CONF_VERIFY_SERVER": "verify_server",
        "CONF_QUICK_VOICE_GATE": "quick_voice_gate",
        "DEFAULT_DEVICE_NAME": "HomeAssistant-BTicino-DoorEntry",
        "DEFAULT_PORT": 5228,
        "DEFAULT_SERVER": "sip.example",
        "DEFAULT_VERIFY_SERVER": False,
        "DEFAULT_QUICK_VOICE_GATE": False,
        "CONF_DEBUG_MODE": "debug_mode",
        "CONF_DEVELOPER_MODE": "developer_mode",
        "DEFAULT_DEBUG_MODE": "off",
        "DEFAULT_DEVELOPER_MODE": False,
        "CONF_SHOW_CLOUD_STATUS": "show_cloud_status",
        "CONF_SHOW_SIP_MONITOR": "show_sip_monitor",
        "CONF_SHOW_CALL_MONITOR": "show_call_monitor",
        "CONF_SHOW_MEDIA_MONITOR": "show_media_monitor",
        "CONF_SHOW_ADVANCED_DIAGNOSTICS": "show_advanced_diagnostics",
        "DEFAULT_SHOW_CLOUD_STATUS": True,
        "DEFAULT_SHOW_SIP_MONITOR": True,
        "DEFAULT_SHOW_CALL_MONITOR": True,
        "DEFAULT_SHOW_MEDIA_MONITOR": True,
        "DEFAULT_SHOW_ADVANCED_DIAGNOSTICS": True,
        "DEBUG_MODE_OFF": "off",
        "DEBUG_MODE_SUPPORT": "support",
        "DEBUG_MODE_DEEP": "deep",
        "DOMAIN": "btdoor_security_plus",
    }
    for key, value in values.items():
        setattr(const, key, value)
    monkeypatch.setitem(sys.modules, const.__name__, const)


def _load(monkeypatch):
    _install_stubs(monkeypatch)
    name = "custom_components.btdoor_security_plus.config_flow"
    sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(name, COMPONENT / "config_flow.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    original_init = module.BticinoDoorEntryConfigFlow.__init__

    def initialized_flow(self):
        _FlowBase.__init__(self)
        original_init(self)

    module.BticinoDoorEntryConfigFlow.__init__ = initialized_flow
    return module


@pytest.fixture
def module(monkeypatch):
    return _load(monkeypatch)


@pytest.fixture
def user_input():
    return {"email": "user@example.com", "password": "secret", "device_name": "HA Door"}


@pytest.mark.asyncio
async def test_user_initial_form(module):
    flow = module.BticinoDoorEntryConfigFlow()
    result = await flow.async_step_user()
    assert result["type"] == "form" and result["step_id"] == "user"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (CloudAuthError, "invalid_cloud_auth"),
        (CloudConnectionError, "cannot_connect_cloud"),
        (CloudError, "cloud_error"),
        (RuntimeError, "unknown"),
    ],
)
async def test_user_error_mapping(module, user_input, error, expected):
    flow = module.BticinoDoorEntryConfigFlow()

    async def fail(_):
        raise error()

    flow._async_discover = fail
    result = await flow.async_step_user(user_input)
    assert result["errors"]["base"] == expected


@pytest.mark.asyncio
async def test_user_no_gateways(module, user_input):
    flow = module.BticinoDoorEntryConfigFlow()

    async def discover(_):
        return []

    flow._async_discover = discover
    result = await flow.async_step_user(user_input)
    assert result["errors"]["base"] == "no_gateways"


@pytest.mark.asyncio
async def test_user_single_gateway_success(module, user_input):
    flow = module.BticinoDoorEntryConfigFlow()
    gateway = _Gateway()

    async def discover(_):
        return [gateway]

    async def finish(selected):
        return {"type": "create_entry", "selected": selected.gateway_id}

    flow._async_discover = discover
    flow._async_finish = finish
    result = await flow.async_step_user(user_input)
    assert result == {"type": "create_entry", "selected": "gw-1"}


@pytest.mark.asyncio
async def test_user_multiple_gateways_and_selection(module, user_input):
    flow = module.BticinoDoorEntryConfigFlow()
    gateways = [_Gateway(gateway_id="gw-1"), _Gateway(gateway_id="gw-2", gateway_name="Side")]

    async def discover(_):
        return gateways

    flow._async_discover = discover
    result = await flow.async_step_user(user_input)
    assert result["step_id"] == "select_gateway"

    async def finish(selected):
        return {"type": "create_entry", "selected": selected.gateway_id}

    flow._async_finish = finish
    result = await flow.async_step_select_gateway({"gateway_id": "gw-2"})
    assert result["selected"] == "gw-2"


@pytest.mark.asyncio
async def test_finish_duplicate_prevention(module, user_input):
    flow = module.BticinoDoorEntryConfigFlow()
    flow._credentials = user_input
    flow._configured_unique_ids.add("gw-1")

    # Match Home Assistant's abort contract explicitly in this harness.
    def abort_if_configured():
        if flow._unique_id in flow._configured_unique_ids:
            raise RuntimeError("already_configured")

    flow._abort_if_unique_id_configured = abort_if_configured
    with pytest.raises(RuntimeError, match="already_configured"):
        await flow._async_finish(_Gateway())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (CloudAuthError, "invalid_cloud_auth"),
        (CloudConnectionError, "cannot_connect_cloud"),
        (SipAuthError, "invalid_auth"),
        (SipConnectionError, "cannot_connect"),
        (CloudError, "provisioning_error"),
        (SipError, "provisioning_error"),
        (RuntimeError, "unknown"),
    ],
)
async def test_finish_provisioning_error_mapping(module, user_input, error, expected):
    flow = module.BticinoDoorEntryConfigFlow()
    flow._credentials = user_input

    async def fail(_):
        raise error()

    flow._async_provision_and_validate = fail
    result = await flow._async_finish(_Gateway())
    assert result["errors"]["base"] == expected


@pytest.mark.asyncio
async def test_finish_creates_entry(module, user_input):
    flow = module.BticinoDoorEntryConfigFlow()
    flow._credentials = user_input

    async def provision(_):
        return {"gateway_id": "gw-1", "email": user_input["email"]}

    flow._async_provision_and_validate = provision
    result = await flow._async_finish(_Gateway())
    assert result["type"] == "create_entry"
    assert result["data"]["gateway_id"] == "gw-1"


@pytest.mark.asyncio
async def test_reauth_success_and_failure(module):
    entry = types.SimpleNamespace(
        data={"email": "old@example.com", "gateway_id": "gw-1", "id_device": "id"}
    )
    flow = module.BticinoDoorEntryConfigFlow()
    flow._reauth_entry = entry

    async def discover(_):
        return [_Gateway()]

    async def provision(_):
        return {"gateway_id": "gw-1", "email": "old@example.com"}

    flow._async_discover = discover
    flow._async_provision_and_validate = provision
    start = await flow.async_step_reauth(entry.data)
    assert start["step_id"] == "reauth_confirm"
    success = await flow.async_step_reauth_confirm({"password": "new"})
    assert success["reason"] == "reconfigure_successful"

    async def reject(_):
        raise CloudAuthError()

    flow._async_discover = reject
    failed = await flow.async_step_reauth_confirm({"password": "bad"})
    assert failed["errors"]["base"] == "invalid_cloud_auth"


@pytest.mark.asyncio
async def test_reconfigure_success_and_wrong_gateway(module):
    entry = types.SimpleNamespace(
        data={"email": "old@example.com", "gateway_id": "gw-1", "id_device": "id"},
        unique_id="gw-1",
    )
    flow = module.BticinoDoorEntryConfigFlow()
    flow._reconfigure_entry_for_test = entry

    async def discover(_):
        return [_Gateway()]

    async def provision(_):
        return {"gateway_id": "gw-1"}

    flow._async_discover = discover
    flow._async_provision_and_validate = provision
    result = await flow.async_step_reconfigure({"email": "new@example.com", "password": "new"})
    assert result["reason"] == "reconfigure_successful"

    async def missing(_):
        return [_Gateway(gateway_id="other")]

    flow._async_discover = missing
    failed = await flow.async_step_reconfigure({"email": "new@example.com", "password": "new"})
    assert failed["errors"]["base"] == "provisioning_error"


@pytest.mark.asyncio
async def test_options_validation_and_confirmation(module):
    flow = module.BTDoorOptionsFlow()
    invalid = await flow.async_step_init(
        {"developer_mode": False, "show_advanced_diagnostics": True}
    )
    assert "show_advanced_diagnostics" in invalid["errors"]

    confirm = await flow.async_step_init(
        {"developer_mode": True, "show_advanced_diagnostics": True, "quick_voice_gate": True}
    )
    assert confirm["step_id"] == "confirm_quick_voice"
    saved = await flow.async_step_confirm_quick_voice({"confirm": True})
    assert saved["type"] == "create_entry" and saved["data"]["quick_voice_gate"] is True


@pytest.mark.asyncio
async def test_qs16_discover_and_validate_helpers(module, monkeypatch, user_input):
    calls = []

    class CloudClient:
        def __init__(self, session, *, email, password):
            calls.append((session, email, password))

        async def async_login(self):
            calls.append("login")

        async def async_list_gateways(self):
            return [_Gateway()]

    module.BticinoCloudClient = CloudClient
    flow = module.BticinoDoorEntryConfigFlow()
    assert (await flow._async_discover(user_input))[0].gateway_id == "gw-1"
    assert calls[-1] == "login"

    sip_calls = []

    class SipClient:
        def __init__(self, **kwargs):
            sip_calls.append(kwargs)

        async def async_test_connection(self):
            sip_calls.append("tested")

    module.BticinoSipClient = SipClient
    data = {
        "sip_account": "sip:user",
        "sip_password": "pw",
        "gateway_id": "gw-1",
        "client_cert_path": "/tmp/cert",
        "client_key_path": "/tmp/key",
        "server": "sip.local",
        "port": "5070",
        "verify_server": True,
    }
    await module._validate_sip(data)
    assert sip_calls[0]["port"] == 5070 and sip_calls[-1] == "tested"


@pytest.mark.asyncio
async def test_qs16_provision_builds_complete_data(module, monkeypatch, user_input):
    provisioned = types.SimpleNamespace(
        device_name="Device",
        plant_id="p",
        plant_name="Plant",
        gateway_id="gw-1",
        gateway_name="Gate",
        id_device="id",
        sip_account="sip:a",
        sip_password="pw",
        client_cert_path="/tmp/cert",
        client_key_path="/tmp/key",
        certificate_not_after="2030-01-01T00:00:00+00:00",
        ca_chain_path="/tmp/ca",
    )

    class CloudClient:
        def __init__(self, *args, **kwargs):
            pass

        async def async_login(self):
            pass

        async def async_provision(self, **kwargs):
            assert kwargs["selection"].gateway_id == "gw-1"
            assert kwargs["device_name"] == "HA Door"
            return provisioned

    module.BticinoCloudClient = CloudClient
    validated = []

    async def validate(data):
        validated.append(data)

    monkeypatch.setattr(module, "_validate_sip", validate)
    flow = module.BticinoDoorEntryConfigFlow()
    flow._credentials = user_input
    data = await flow._async_provision_and_validate(_Gateway())
    assert data["ca_chain_path"] == "/tmp/ca"
    assert data["port"] == 5228 and validated == [data]


@pytest.mark.asyncio
async def test_qs16_reauth_residual_error_mapping(module):
    entry = types.SimpleNamespace(data={"email": "old@example.com", "gateway_id": "gw-1"})
    mapping = [
        (CloudConnectionError, "cannot_connect_cloud"),
        (CloudError, "provisioning_error"),
        (SipError, "provisioning_error"),
    ]
    for error, expected in mapping:
        flow = module.BticinoDoorEntryConfigFlow()
        flow._reauth_entry = entry

        async def fail(_, exc=error):
            raise exc()

        flow._async_discover = fail
        result = await flow.async_step_reauth_confirm({"password": "new"})
        assert result["errors"]["base"] == expected

    flow = module.BticinoDoorEntryConfigFlow()
    flow._reauth_entry = entry

    async def missing(_):
        return [_Gateway(gateway_id="other")]

    flow._async_discover = missing
    result = await flow.async_step_reauth_confirm({"password": "new"})
    assert result["errors"]["base"] == "provisioning_error"


@pytest.mark.asyncio
async def test_qs16_options_normalization_and_confirmation_form(module):
    flow = module.BTDoorOptionsFlow()
    flow.config_entry.options = {"quick_voice_gate": False}
    result = await flow.async_step_init(
        {
            "developer_mode": False,
            "show_advanced_diagnostics": False,
            "quick_voice_gate": False,
        }
    )
    assert result["data"]["show_advanced_diagnostics"] is False
    confirm_form = await flow.async_step_confirm_quick_voice()
    assert confirm_form["step_id"] == "confirm_quick_voice"
