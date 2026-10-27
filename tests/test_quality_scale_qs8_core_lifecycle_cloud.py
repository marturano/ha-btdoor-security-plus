"""QS-8 behavioural coverage for core lifecycle and cloud renewal branches."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _reset_package() -> None:
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus") or name.startswith(
            "homeassistant"
        ):
            sys.modules.pop(name, None)
    root = types.ModuleType("custom_components")
    root.__path__ = [str(ROOT / "custom_components")]
    sys.modules[root.__name__] = root
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG)]
    sys.modules[package.__name__] = package


def _load(name: str):
    full = f"custom_components.btdoor_security_plus.{name}"
    spec = importlib.util.spec_from_file_location(full, PKG / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def _install_ha_stubs() -> None:
    ha = types.ModuleType("homeassistant")
    ce = types.ModuleType("homeassistant.config_entries")
    ce.ConfigEntry = object
    core = types.ModuleType("homeassistant.core")
    core.CoreState = SimpleNamespace(running="running")
    core.HomeAssistant = object
    exc = types.ModuleType("homeassistant.exceptions")
    exc.ConfigEntryAuthFailed = type("ConfigEntryAuthFailed", (Exception,), {})
    exc.ConfigEntryNotReady = type("ConfigEntryNotReady", (Exception,), {})
    helpers = types.ModuleType("homeassistant.helpers")
    typing_mod = types.ModuleType("homeassistant.helpers.typing")
    typing_mod.ConfigType = dict
    issue = types.ModuleType("homeassistant.helpers.issue_registry")
    issue.IssueSeverity = SimpleNamespace(WARNING="warning")
    issue.async_create_issue = lambda *a, **k: None
    issue.async_delete_issue = lambda *a, **k: None
    entity = types.ModuleType("homeassistant.helpers.entity_registry")
    entity.async_get = lambda hass: hass.entity_registry
    storage = types.ModuleType("homeassistant.helpers.storage")
    storage.Store = object
    aio = types.ModuleType("homeassistant.helpers.aiohttp_client")
    aio.async_get_clientsession = lambda hass: "session"
    event = types.ModuleType("homeassistant.helpers.event")
    event.async_track_time_interval = lambda *a, **k: lambda: None
    sys.modules.update(
        {
            m.__name__: m
            for m in [ha, ce, core, exc, helpers, typing_mod, issue, entity, storage, aio, event]
        }
    )


@pytest.fixture
def init_module():
    _reset_package()
    _install_ha_stubs()
    _load("const")
    return _load("__init__")


class Config:
    def __init__(self, root: Path):
        self.root = root
        self.language = "it"

    def path(self, *parts):
        return str(self.root.joinpath(*parts))


@pytest.mark.asyncio
async def test_unload_entry_releases_all_runtime_resources(init_module):
    events = []
    runtime = SimpleNamespace(
        event_bus=SimpleNamespace(publish=lambda event: events.append(event)),
        renewal_unsub=lambda: events.append("renewal_unsub"),
        event_unsub=lambda: events.append("event_unsub"),
        store=SimpleNamespace(async_save=AsyncMock()),
        client=SimpleNamespace(export_state=lambda: {"ok": True}, async_stop=AsyncMock()),
        debug=SimpleNamespace(async_stop=AsyncMock()),
    )
    entry = SimpleNamespace(entry_id="entry", runtime_data=runtime)
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_unload_platforms=AsyncMock(return_value=True))
    )
    assert await init_module.async_unload_entry(hass, entry) is True
    runtime.store.async_save.assert_awaited_once_with({"ok": True})
    runtime.client.async_stop.assert_awaited_once()
    runtime.debug.async_stop.assert_awaited_once()
    assert "renewal_unsub" in events and "event_unsub" in events

    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)
    assert await init_module.async_unload_entry(hass, entry) is False


@pytest.mark.asyncio
async def test_debug_and_certificate_storage_migrations(init_module, tmp_path):
    hass = SimpleNamespace(
        config=Config(tmp_path),
        config_entries=SimpleNamespace(async_update_entry=lambda *a, **k: None),
    )
    entry = SimpleNamespace(entry_id="entry", data={init_module.CONF_GATEWAY_ID: "gw"})
    legacy = tmp_path / init_module.DOMAIN / "logs" / "entry"
    legacy.mkdir(parents=True)
    (legacy / "debug.log").write_text("log")
    await init_module._async_migrate_debug_storage(hass, entry)
    assert (
        tmp_path / "custom_components" / init_module.DOMAIN / "logs" / "entry" / "debug.log"
    ).read_text() == "log"

    source = tmp_path / "btdoor_security_plus" / "gw"
    source.mkdir(parents=True)
    (source / "client-cert.pem").write_text("cert")
    (source / "client-key.pem").write_text("key")
    updated = {}
    hass.config_entries.async_update_entry = lambda _entry, data: updated.update(data)
    await init_module._async_migrate_certificate_storage(hass, entry)
    assert await asyncio.to_thread(Path(updated[init_module.CONF_CLIENT_CERT_PATH]).is_file)
    assert await asyncio.to_thread(Path(updated[init_module.CONF_CLIENT_KEY_PATH]).is_file)

    entry_no_gateway = SimpleNamespace(data={})
    await init_module._async_migrate_certificate_storage(hass, entry_no_gateway)


@pytest.mark.asyncio
async def test_certificate_renewal_success_and_nonrenewal(init_module, monkeypatch, tmp_path):
    cloud = types.ModuleType("custom_components.btdoor_security_plus.cloud")
    cloud.BticinoCloudAuthenticationError = type(
        "BticinoCloudAuthenticationError", (Exception,), {}
    )
    cloud.BticinoCloudConnectionError = type("BticinoCloudConnectionError", (Exception,), {})
    cloud.BticinoCloudError = type("BticinoCloudError", (Exception,), {})
    cloud.PlantGateway = lambda **kwargs: SimpleNamespace(**kwargs)
    cloud.certificate_expiry = lambda path: None
    provisioned = SimpleNamespace(
        sip_account="sip:new",
        sip_password="pw",
        client_cert_path="/new/cert",
        client_key_path="/new/key",
        certificate_not_after="2030-01-01T00:00:00Z",
        id_device="device",
    )
    client = SimpleNamespace(
        async_login=AsyncMock(), async_provision=AsyncMock(return_value=provisioned)
    )
    cloud.BticinoCloudClient = lambda *a, **k: client
    sys.modules[cloud.__name__] = cloud

    fired = []
    updated = {}
    hass = SimpleNamespace(
        config=Config(tmp_path),
        bus=SimpleNamespace(async_fire=lambda *a: fired.append(a)),
        config_entries=SimpleNamespace(
            async_update_entry=lambda _entry, data: updated.update(data)
        ),
    )
    data = {
        init_module.CONF_EMAIL: "user@example.com",
        init_module.CONF_PASSWORD: "secret",
        init_module.CONF_GATEWAY_ID: "gw",
        init_module.CONF_PLANT_ID: "p",
        init_module.CONF_PLANT_NAME: "Plant",
        init_module.CONF_GATEWAY_NAME: "Door",
        init_module.CONF_DEVICE_NAME: "Device",
        init_module.CONF_ID_DEVICE: "old",
    }
    entry = SimpleNamespace(entry_id="entry", data=data)
    assert await init_module._async_renew_certificate_if_needed(hass, entry) is True
    assert updated[init_module.CONF_SIP_ACCOUNT] == "sip:new"
    assert fired[-1][1]["event_type"] == "certificate_renewed"

    cloud.certificate_expiry = lambda path: datetime.now(UTC) + timedelta(days=365)
    assert await init_module._async_renew_certificate_if_needed(hass, entry) is False
    assert (
        await init_module._async_renew_certificate_if_needed(
            hass, SimpleNamespace(data={}, entry_id="x")
        )
        is False
    )


@pytest.mark.asyncio
async def test_certificate_renewal_error_paths(init_module, tmp_path):
    cloud = types.ModuleType("custom_components.btdoor_security_plus.cloud")
    Auth = type("BticinoCloudAuthenticationError", (Exception,), {})
    Conn = type("BticinoCloudConnectionError", (Exception,), {})
    Generic = type("BticinoCloudError", (Exception,), {})
    cloud.BticinoCloudAuthenticationError = Auth
    cloud.BticinoCloudConnectionError = Conn
    cloud.BticinoCloudError = Generic
    cloud.PlantGateway = lambda **kwargs: SimpleNamespace(**kwargs)
    cloud.certificate_expiry = lambda path: None
    sys.modules[cloud.__name__] = cloud
    hass = SimpleNamespace(
        config=Config(tmp_path),
        bus=SimpleNamespace(async_fire=lambda *a: None),
        config_entries=SimpleNamespace(async_update_entry=lambda *a, **k: None),
    )
    base = {
        init_module.CONF_EMAIL: "u",
        init_module.CONF_PASSWORD: "p",
        init_module.CONF_GATEWAY_ID: "gw",
    }

    for exc_type, expected in [
        (Auth, init_module.ConfigEntryAuthFailed),
        (Conn, init_module.ConfigEntryNotReady),
        (Generic, init_module.ConfigEntryNotReady),
    ]:
        failing = SimpleNamespace(
            async_login=AsyncMock(side_effect=exc_type("boom")), async_provision=AsyncMock()
        )
        cloud.BticinoCloudClient = lambda *a, _f=failing, **k: _f
        with pytest.raises(expected):
            await init_module._async_renew_certificate_if_needed(
                hass, SimpleNamespace(entry_id="e", data=dict(base))
            )

    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    cert.write_text("c")
    key.write_text("k")
    existing = dict(
        base,
        **{
            init_module.CONF_CLIENT_CERT_PATH: str(cert),
            init_module.CONF_CLIENT_KEY_PATH: str(key),
        },
    )
    failing = SimpleNamespace(
        async_login=AsyncMock(side_effect=Conn("offline")), async_provision=AsyncMock()
    )
    cloud.BticinoCloudClient = lambda *a, **k: failing
    assert (
        await init_module._async_renew_certificate_if_needed(
            hass, SimpleNamespace(entry_id="e", data=existing)
        )
        is False
    )


@pytest.mark.asyncio
async def test_entry_migration_update_listener_and_global_setup(init_module, monkeypatch):
    updates = []
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_update_entry=lambda *a, **k: updates.append(k), async_reload=AsyncMock()
        )
    )
    entry = SimpleNamespace(version=1, data={}, title="Door", entry_id="entry")
    assert await init_module.async_migrate_entry(hass, entry) is True
    assert (
        updates[-1]["version"] == 2 and updates[-1]["data"][init_module.CONF_DEVICE_NAME] == "Door"
    )
    await init_module._async_update_listener(hass, entry)
    hass.config_entries.async_reload.assert_awaited_once_with("entry")

    sentences = types.ModuleType("custom_components.btdoor_security_plus.sentence_manager")
    sentences.async_install_sentences = AsyncMock(return_value={"installed": 0, "updated": 0})
    services = types.ModuleType("custom_components.btdoor_security_plus.services")
    services.async_register_services = AsyncMock()
    voice = types.ModuleType("custom_components.btdoor_security_plus.voice")
    voice.async_register_voice_intents = lambda h: updates.append({"voice": True})
    sys.modules.update({m.__name__: m for m in (sentences, services, voice)})
    hass.state = "starting"
    assert await init_module.async_setup(hass, {}) is True
    services.async_register_services.assert_awaited_once()
