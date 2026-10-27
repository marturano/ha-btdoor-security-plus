"""QS-7 behavioural coverage for lifecycle and SIP transport."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _reset_package() -> None:
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus"):
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


@pytest.fixture
def sip():
    _reset_package()
    _load("const")
    _load("sip_identity")
    _load("media")
    return _load("sip_client")


def _client(sip):
    return sip.BticinoSipClient(
        sip_account="sip:user@example.com",
        sip_password="secret",
        gateway_id="gw",
        client_cert_path="/tmp/cert.pem",
        client_key_path="/tmp/key.pem",
        server="sip.example.com",
        port=5061,
        verify_server=False,
    )


class Writer:
    def __init__(self, closing=False):
        self.closing = closing
        self.data = []
        self.closed = False

    def is_closing(self):
        return self.closing

    def write(self, data):
        self.data.append(data)

    async def drain(self):
        return None

    def close(self):
        self.closed = True
        self.closing = True

    async def wait_closed(self):
        return None


class Reader:
    def __init__(self, eof=False):
        self.eof = eof

    def at_eof(self):
        return self.eof


@pytest.mark.asyncio
async def test_start_stop_and_live_connection_probe(sip, monkeypatch):
    client = _client(sip)
    session = sip.SipSession(Reader(), Writer(), "sip:u", "sip:c", "sip:p", "u")
    client._async_ensure_session = AsyncMock(return_value=session)
    client._async_keepalive_loop = AsyncMock()
    await client.async_start()
    assert client._async_ensure_session.await_count == 1
    assert client._keepalive_task is not None
    await asyncio.sleep(0)

    client.registered = True
    client.last_status = "SIP/2.0 200 OK"
    client._session = session
    result = await client.async_test_connection()
    assert result.code == 200

    client._async_drop_session = AsyncMock()
    client._release_media_preparation = lambda *a, **k: None
    await client.async_stop()
    client._async_drop_session.assert_awaited_once()
    assert client._keepalive_task is None


@pytest.mark.asyncio
async def test_connection_probe_uses_temporary_register_and_restores_state(sip):
    client = _client(sip)
    writer = Writer()
    session = sip.SipSession(Reader(), writer, "i", "c", "p", "u")
    client.registered = False
    client.connected_at = datetime.now(UTC)
    client._ever_registered = True
    client.reconnect_count = 4
    client._async_register = AsyncMock(return_value=(session, sip.SipResult("SIP/2.0 200 OK", 200)))
    client._async_close_raw = AsyncMock()
    result = await client.async_test_connection()
    assert result.code == 200
    assert client.registered is False and client._ever_registered is True
    assert client.reconnect_count == 4
    client._async_close_raw.assert_awaited_once_with(writer)


@pytest.mark.asyncio
async def test_open_gate_success_and_retry_paths(sip, monkeypatch):
    client = _client(sip)
    session = sip.SipSession(Reader(), Writer(), "i", "c", "p", "u")
    client._async_ensure_session = AsyncMock(return_value=session)
    client._async_send_message = AsyncMock(return_value=sip.SipResult("SIP/2.0 202 Accepted", 202))
    events = []
    client.add_listener(lambda event, data: events.append((event, data)))
    result = await client.async_open_gate()
    assert result.code == 202 and client.last_error is None
    assert events[-1][0] == "gate_opened"

    client._async_send_message = AsyncMock(
        side_effect=[sip.BticinoSipNotFoundError("404"), sip.SipResult("SIP/2.0 200 OK", 200)]
    )
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    result = await client.async_open_gate()
    assert result.code == 200 and client._async_send_message.await_count == 2


@pytest.mark.asyncio
async def test_open_gate_authentication_failure_notifies(sip, monkeypatch):
    client = _client(sip)
    session = sip.SipSession(Reader(), Writer(), "i", "c", "p", "u")
    client._async_ensure_session = AsyncMock(return_value=session)
    client._async_send_message = AsyncMock(side_effect=sip.BticinoSipAuthenticationError("403"))
    client._async_drop_session = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    events = []
    client.add_listener(lambda event, data: events.append((event, data)))
    with pytest.raises(sip.BticinoSipAuthenticationError):
        await client.async_open_gate()
    assert client._async_drop_session.await_count == 2
    assert events[-1][0] == "gate_open_failed"


@pytest.mark.asyncio
async def test_reject_call_and_ensure_session(sip):
    client = _client(sip)
    with pytest.raises(sip.BticinoSipError):
        await client.async_reject_call()

    writer = Writer()
    session = sip.SipSession(Reader(), writer, "i", "c", "p", "u")
    client.ringing = True
    client._invite_headers = {
        "via": ["v"],
        "from": ["f"],
        "to": ["t"],
        "call-id": ["id"],
        "cseq": ["1 INVITE"],
    }
    client._invite_local_tag = "tag"
    client.last_caller = "door"
    client.last_call_id = "id"
    client.call_started_at = datetime.now(UTC)
    client._session = session
    client.registered = True
    client._async_send_response = AsyncMock()
    result = await client.async_reject_call()
    assert result.code == 486 and client.call_state == "rejected"
    assert client._invite_headers is None

    client2 = _client(sip)
    client2._async_drop_session = AsyncMock()
    new_session = sip.SipSession(Reader(), Writer(), "i", "c", "p", "u")
    client2._async_register = AsyncMock(return_value=(new_session, sip.SipResult("ok", 200)))
    client2._async_reader_loop = AsyncMock()
    ensured = await client2._async_ensure_session()
    assert ensured is new_session and client2._session is new_session
    await asyncio.sleep(0)
    if client2._reader_task:
        await client2._reader_task


@pytest.mark.asyncio
async def test_drop_session_write_exchange_and_connect_errors(sip, monkeypatch, tmp_path):
    client = _client(sip)
    writer = Writer()
    session = sip.SipSession(Reader(), writer, "i", "c", "p", "u")
    client._session = session
    client.registered = True
    pending = asyncio.get_running_loop().create_future()
    client._pending[("id", "MESSAGE")] = pending
    events = []
    client.add_listener(lambda event, data: events.append(event))
    await client._async_drop_session()
    assert writer.closed and isinstance(pending.exception(), sip.BticinoSipConnectionError)
    assert "disconnected" in events

    writer2 = Writer()
    await client._async_write(writer2, b"abc")
    assert writer2.data == [b"abc"]

    session2 = sip.SipSession(Reader(), Writer(), "i", "c", "p", "u")

    async def complete(writer, data):
        key = next(iter(client._pending))
        client._pending[key].set_result((b"raw", "SIP/2.0 200 OK", {}))

    client._async_write = complete
    raw, status, headers = await client._async_exchange(
        session2, b"x", call_id="c", cseq_method="MESSAGE", timeout=1
    )
    assert status.endswith("200 OK") and not client._pending

    client.client_cert_path = str(tmp_path / "missing-cert")
    client.client_key_path = str(tmp_path / "missing-key")
    with pytest.raises(sip.BticinoSipConnectionError, match="certificate"):
        await client._async_connect()
    (tmp_path / "missing-cert").write_text("x")
    with pytest.raises(sip.BticinoSipConnectionError, match="key"):
        await client._async_connect()


@pytest.mark.asyncio
async def test_send_message_authentication_and_errors(sip):
    client = _client(sip)
    session = sip.SipSession(Reader(), Writer(), "sip:i", "sip:c", "sip:p", "u")
    client._async_exchange = AsyncMock(
        side_effect=[
            (
                b"raw",
                "SIP/2.0 407 Proxy Authentication Required",
                {"proxy-authenticate": ['Digest realm="r", nonce="n"']},
            ),
            (b"raw", "SIP/2.0 202 Accepted", {}),
        ]
    )
    result = await client._async_send_message(session, "sip:t", "OPEN")
    assert result.code == 202 and client._message_challenge

    client._async_exchange = AsyncMock(return_value=(b"raw404", "SIP/2.0 404 Not Found", {}))
    client._message_challenge = None
    with pytest.raises(sip.BticinoSipNotFoundError):
        await client._async_send_message(session, "sip:t", "OPEN")
