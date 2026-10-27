"""QS-19 behavioural coverage for lifecycle helpers and SIP stream framing."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from test_quality_scale_qs8_core_lifecycle_cloud import (
    Config,
    _install_ha_stubs,
    _load,
    _reset_package,
)


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
        if (
            name == "custom_components"
            or name.startswith("custom_components.btdoor_security_plus")
            or name.startswith("homeassistant")
        ):
            sys.modules.pop(name, None)
    sys.modules.update(tracked)


def _init_module():
    _reset_package()
    _install_ha_stubs()
    _load("const")
    return _load("__init__")


def _sip_module():
    _reset_package()
    _load("const")
    _load("sip_identity")
    _load("media")
    return _load("sip_client")


@pytest.mark.asyncio
async def test_setup_services_migration_and_update_listener(tmp_path, monkeypatch):
    module = _init_module()
    calls: list[object] = []

    sentence = __import__("types").ModuleType(
        "custom_components.btdoor_security_plus.sentence_manager"
    )
    sentence.async_install_sentences = AsyncMock(return_value={"installed": 1, "updated": 0})
    services = __import__("types").ModuleType("custom_components.btdoor_security_plus.services")
    services.async_register_services = AsyncMock()
    voice = __import__("types").ModuleType("custom_components.btdoor_security_plus.voice")
    voice.async_register_voice_intents = lambda hass: calls.append("voice")
    sys.modules.update(
        {sentence.__name__: sentence, services.__name__: services, voice.__name__: voice}
    )

    module.ir.async_create_issue = lambda *a, **k: calls.append("create")
    module.ir.async_delete_issue = lambda *a, **k: calls.append("delete")
    hass = SimpleNamespace(state=module.CoreState.running)
    assert await module.async_setup(hass, {}) is True
    assert "create" in calls and "voice" in calls

    calls.clear()
    hass.state = "starting"
    sentence.async_install_sentences.return_value = {"installed": 0, "updated": 0}
    assert await module.async_setup(hass, {}) is True
    assert "delete" in calls

    updated = []
    config_entries = SimpleNamespace(
        async_update_entry=lambda *a, **k: updated.append(k),
        async_reload=AsyncMock(),
    )
    hass = SimpleNamespace(config=Config(tmp_path), config_entries=config_entries)
    entry = SimpleNamespace(version=1, title="Door", data={}, entry_id="entry")
    assert await module.async_migrate_entry(hass, entry) is True
    assert updated[-1]["version"] == 2
    entry.version = 2
    assert await module.async_migrate_entry(hass, entry) is True
    await module._async_update_listener(hass, entry)
    config_entries.async_reload.assert_awaited_once_with("entry")


@pytest.mark.asyncio
async def test_storage_edge_branches_and_unload_optional_resources(tmp_path):
    module = _init_module()
    hass = SimpleNamespace(
        config=Config(tmp_path),
        config_entries=SimpleNamespace(async_update_entry=lambda *a, **k: None),
    )

    # Existing destination files take precedence; fullchain is migrated too.
    source = tmp_path / "source"
    source.mkdir()
    destination = tmp_path / "destination"
    destination.mkdir()
    for name in ("client-cert.pem", "client-key.pem", "ca-chain.pem", "client-fullchain.pem"):
        (source / name).write_text(name)
    (destination / "client-cert.pem").write_text("existing")
    result = module._copy_certificate_material(source, destination)
    assert await asyncio.to_thread(Path(result[module.CONF_CLIENT_KEY_PATH]).is_file)
    assert (destination / "client-fullchain.pem").is_file()

    # Already migrated material exits without rewriting the config entry.
    cert_dir = Path(module._certificate_storage_dir(hass, "gw"))
    await asyncio.to_thread(cert_dir.mkdir, parents=True)
    cert = cert_dir / "client-cert.pem"
    key = cert_dir / "client-key.pem"
    cert.write_text("cert")
    key.write_text("key")
    entry = SimpleNamespace(
        data={
            module.CONF_GATEWAY_ID: "gw",
            module.CONF_CLIENT_CERT_PATH: str(cert),
            module.CONF_CLIENT_KEY_PATH: str(key),
        }
    )
    await module._async_migrate_certificate_storage(hass, entry)

    runtime = SimpleNamespace(
        event_bus=None,
        renewal_unsub=None,
        event_unsub=None,
        store=SimpleNamespace(async_save=AsyncMock()),
        client=SimpleNamespace(export_state=lambda: {}, async_stop=AsyncMock()),
        debug=None,
    )
    unload = AsyncMock(return_value=True)
    entry = SimpleNamespace(entry_id="entry", runtime_data=runtime)
    hass.config_entries.async_unload_platforms = unload
    assert await module.async_unload_entry(hass, entry)
    runtime.client.async_stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_sip_stream_frame_and_response_residuals():
    sip = _sip_module()

    reader = asyncio.StreamReader()
    reader.feed_data(b"\r\nINVITE sip:x SIP/2.0\r\nContent-Length: 4\r\n\r\nbody")
    reader.feed_eof()
    raw = await sip.BticinoSipClient._read_sip_frame(reader, 1)
    assert raw.endswith(b"body")
    first, headers, body = sip.BticinoSipClient._parse_message(raw)
    assert first.startswith("INVITE") and headers["content-length"] == ["4"] and body == b"body"
    assert sip.BticinoSipClient._first_header(headers, "missing") == ""

    reader = asyncio.StreamReader()
    reader.feed_data(b"\r\n\r\nnoise\r\n\r\nSIP/2.0 180 Ringing\r\nContent-Length: 0\r\n\r\n")
    reader.feed_eof()
    response = await sip.BticinoSipClient._read_response(reader, 1)
    assert response.startswith(b"SIP/2.0 180")

    reader = asyncio.StreamReader()
    reader.feed_data(b"SIP/2.0 200 OK\r\nContent-Length: 3\r\n\r\nabc")
    reader.feed_eof()
    assert (await sip.BticinoSipClient._read_response(reader, 1)).endswith(b"abc")

    reader = asyncio.StreamReader()
    reader.feed_data(b"SIP/2.0 200 OK\r\nContent-Length: 3\r\n\r\na")
    reader.feed_eof()
    with pytest.raises(sip.BticinoSipConnectionError, match="Incomplete SIP response body"):
        await sip.BticinoSipClient._read_response(reader, 1)

    reader = asyncio.StreamReader()
    reader.feed_data(b"INVITE sip:x SIP/2.0\r\nContent-Length: 3\r\n\r\na")
    reader.feed_eof()
    with pytest.raises(sip.BticinoSipConnectionError, match="Incomplete SIP frame body"):
        await sip.BticinoSipClient._read_sip_frame(reader, 1)


@pytest.mark.asyncio
async def test_read_final_response_skips_provisional(monkeypatch):
    sip = _sip_module()
    client = sip.BticinoSipClient(
        sip_account="sip:user@example.com",
        sip_password="secret",
        gateway_id="gw",
        client_cert_path="cert",
        client_key_path="key",
        server="sip.example",
        port=5061,
        verify_server=True,
    )
    frames = iter(
        [
            b"SIP/2.0 100 Trying\r\nContent-Length: 0\r\n\r\n",
            b"SIP/2.0 200 OK\r\nContent-Length: 0\r\n\r\n",
        ]
    )

    async def read(_reader, _timeout):
        return next(frames)

    monkeypatch.setattr(client, "_read_response", read)
    raw, status, headers = await client._read_final_response(SimpleNamespace(), 1)
    assert (
        status == "SIP/2.0 200 OK"
        and raw.startswith(b"SIP/2.0 200")
        and headers["content-length"] == ["0"]
    )


@pytest.mark.asyncio
async def test_failed_setup_cleanup_releases_all_runtime_resources(tmp_path):
    module = _init_module()
    calls: list[str] = []
    runtime = SimpleNamespace(
        renewal_unsub=lambda: calls.append("renewal_unsub"),
        event_unsub=lambda: calls.append("event_unsub"),
        client=SimpleNamespace(async_stop=AsyncMock()),
        debug=SimpleNamespace(async_stop=AsyncMock()),
    )

    await module._async_cleanup_runtime(runtime)

    assert calls == ["renewal_unsub", "event_unsub"]
    assert runtime.renewal_unsub is None
    assert runtime.event_unsub is None
    runtime.client.async_stop.assert_awaited_once()
    runtime.debug.async_stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_sip_stop_awaits_call_timeout_task():
    sip = _sip_module()
    client = sip.BticinoSipClient(
        sip_account="sip:user@example.com",
        sip_password="secret",
        gateway_id="gw",
        client_cert_path="cert",
        client_key_path="key",
        server="sip.example",
        port=5061,
        verify_server=True,
    )
    timeout_task = asyncio.create_task(asyncio.sleep(60))
    client._call_timeout_task = timeout_task

    await client.async_stop()

    assert timeout_task.done()
    assert timeout_task.cancelled()
    assert client._call_timeout_task is None
