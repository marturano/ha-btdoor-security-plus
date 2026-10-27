"""QS-13 behavioural coverage for SIP dialog, registration and keepalive."""

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
    previous = {
        name: module
        for name, module in sys.modules.items()
        if name.startswith("custom_components.btdoor_security_plus")
    }
    _reset_package()
    _load("const")
    _load("sip_identity")
    _load("media")
    loaded = _load("sip_client")
    try:
        yield loaded
    finally:
        for name in list(sys.modules):
            if name.startswith("custom_components.btdoor_security_plus"):
                sys.modules.pop(name, None)
        sys.modules.update(previous)


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


class Reader:
    def at_eof(self):
        return False


class Writer:
    def __init__(self):
        self.data = []
        self.closed = False

    def is_closing(self):
        return self.closed

    def write(self, data):
        self.data.append(data)

    async def drain(self):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        return None


def _headers(method="INVITE", call_id="call-13"):
    return {
        "via": ["SIP/2.0/TLS proxy;branch=z9hG4bK1"],
        "from": ["Door <sip:door@example.com>;tag=remote"],
        "to": ["<sip:user@example.com>"],
        "contact": ["<sip:door@example.com>"],
        "call-id": [call_id],
        "cseq": [f"1 {method}"],
        "content-type": ["application/sdp"],
    }


@pytest.mark.asyncio
async def test_invite_sdp_then_cancel_terminates_dialog(sip):
    client = _client(sip)
    writer = Writer()
    session = sip.SipSession(Reader(), writer, "i", "c", "p", "u")
    client._async_send_response = AsyncMock()
    events = []
    client.add_listener(lambda event, data: events.append((event, data)))
    sdp = (
        b"v=0\r\no=- 1 1 IN IP4 10.0.0.2\r\ns=Door\r\nc=IN IP4 10.0.0.2\r\n"
        b"t=0 0\r\nm=audio 4000 RTP/AVP 0\r\na=sendrecv\r\n"
    )
    headers = _headers()
    await client._async_handle_request(
        session, "INVITE sip:user@example.com SIP/2.0", headers, sdp, packet_id=13
    )
    assert client.ringing is True
    assert client.call_state == "ringing"
    assert client.invite_received_count == 1
    assert client.last_sdp_offer is not None
    assert client.sdp_audio_port == 4000
    assert client._async_send_response.await_args_list[0].args[1:3] == (100, "Trying")
    assert client._async_send_response.await_args_list[1].args[1:3] == (180, "Ringing")
    assert any(event == "incoming_call" for event, _ in events)

    cancel = _headers("CANCEL")
    cancel["content-type"] = [""]
    await client._async_handle_request(
        session, "CANCEL sip:user@example.com SIP/2.0", cancel, b"", packet_id=14
    )
    assert client.ringing is False
    assert client.call_state == "missed"
    assert client.dialog_state == "terminated"
    assert client.missed_call_count == 1
    responses = [call.args[1] for call in client._async_send_response.await_args_list]
    assert 200 in responses and 487 in responses
    assert any(event == "call_ended" for event, _ in events)


@pytest.mark.asyncio
async def test_bye_and_timeout_paths(sip, monkeypatch):
    client = _client(sip)
    writer = Writer()
    session = sip.SipSession(Reader(), writer, "i", "c", "p", "u")
    client._async_send_response = AsyncMock()
    client.ringing = False
    client.call_started_at = datetime.now(UTC)
    client.last_call_id = "call-bye"
    client._active_call_id = "call-bye"
    await client._async_handle_request(
        session, "BYE sip:user@example.com SIP/2.0", _headers("BYE", "call-bye"), b""
    )
    assert client.call_state == "ended"

    client2 = _client(sip)
    client2.ringing = True
    client2._active_call_id = "timeout-call"
    client2.last_call_id = "timeout-call"
    client2.last_caller = "Door"
    client2.call_started_at = datetime.now(UTC)
    events = []
    client2.add_listener(lambda event, data: events.append(event))
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    await client2._async_call_timeout("timeout-call")
    assert client2.call_state == "missed"
    assert client2.missed_call_count == 1
    assert events[-2:] == ["call_timeout", "missed_call"]


@pytest.mark.asyncio
async def test_register_challenge_success_and_failure(sip):
    client = _client(sip)
    reader, writer = Reader(), Writer()
    client._async_connect = AsyncMock(return_value=(reader, writer))
    client._async_write = AsyncMock()
    client._read_final_response = AsyncMock(
        side_effect=[
            (
                b"401",
                "SIP/2.0 401 Unauthorized",
                {"www-authenticate": ['Digest realm="r", nonce="n"']},
            ),
            (b"200", "SIP/2.0 200 OK", {}),
        ]
    )
    events = []
    client.add_listener(lambda event, data: events.append(event))
    session, result = await client._async_register()
    assert result.code == 200 and client.registered
    assert session.writer is writer
    assert client._async_write.await_count == 2
    assert events == ["registered"]

    client2 = _client(sip)
    writer2 = Writer()
    client2._async_connect = AsyncMock(return_value=(Reader(), writer2))
    client2._async_write = AsyncMock()
    client2._read_final_response = AsyncMock(return_value=(b"403", "SIP/2.0 403 Forbidden", {}))
    with pytest.raises(sip.BticinoSipAuthenticationError):
        await client2._async_register()
    assert writer2.closed is True


@pytest.mark.asyncio
async def test_prime_proxy_auth_keepalive_and_response_building(sip, monkeypatch):
    client = _client(sip)
    writer = Writer()
    session = sip.SipSession(Reader(), writer, "i", "c", "p", "u")
    client._session = session
    client._async_write = AsyncMock()
    client._read_final_response = AsyncMock(
        return_value=(
            b"407",
            "SIP/2.0 407 Proxy Authentication Required",
            {"proxy-authenticate": ['Digest realm="r", nonce="n"']},
        )
    )
    await client._async_prime_proxy_auth()
    assert client._message_challenge is not None
    assert client._message_auth_name == "Proxy-Authorization"

    client._async_ensure_session = AsyncMock(return_value=session)
    sleeps = 0

    async def one_sleep(_):
        nonlocal sleeps
        sleeps += 1
        if sleeps > 1:
            raise asyncio.CancelledError

    monkeypatch.setattr(asyncio, "sleep", one_sleep)
    with pytest.raises(asyncio.CancelledError):
        await client._async_keepalive_loop()
    assert client.last_keepalive_at is not None

    client._async_write = AsyncMock()
    await client._async_send_response(
        writer, 200, "OK", _headers("OPTIONS"), add_to_tag=True, to_tag="local"
    )
    payload = client._async_write.await_args.args[1].decode()
    assert payload.startswith("SIP/2.0 200 OK")
    assert "To: <sip:user@example.com>;tag=local" in payload
    assert "Content-Length: 0" in payload
