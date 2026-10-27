"""QS-12 behavioural coverage for cloud transport and SIP dispatch."""

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


class Writer:
    def __init__(self):
        self.closed = False
        self.data = []

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


@pytest.mark.asyncio
async def test_sip_request_dispatch_branches(sip):
    client = _client(sip)
    writer = Writer()
    session = sip.SipSession(SimpleNamespace(), writer, "i", "c", "p", "u")
    client._async_send_response = AsyncMock()
    events = []
    client.add_listener(lambda event, data: events.append((event, data)))

    base = {
        "from": ["Door <sip:door@example.com>;tag=from"],
        "to": ["<sip:user@example.com>"],
        "call-id": ["call-1"],
        "cseq": ["1 MESSAGE"],
        "content-type": ["text/plain"],
    }
    await client._async_handle_request(session, "BROKEN", base, b"", packet_id=1)
    assert client.last_sip_method is None

    await client._async_handle_request(
        session, "MESSAGE sip:user SIP/2.0", base, b"hello", packet_id=2
    )
    assert client.last_message == "hello" and client.message_count == 1
    await client._async_handle_request(
        session, "MESSAGE sip:user SIP/2.0", base, b"hello", packet_id=3
    )
    assert client.message_count == 1

    for method in (
        "OPTIONS",
        "ACK",
        "INFO",
        "NOTIFY",
        "REFER",
        "SUBSCRIBE",
        "PRACK",
        "UPDATE",
        "PUBLISH",
    ):
        headers = dict(base)
        headers["cseq"] = [f"2 {method}"]
        headers["event"] = ["door"]
        headers["subscription-state"] = ["active"]
        headers["refer-to"] = ["sip:other@example.com"]
        await client._async_handle_request(
            session, f"{method} sip:user SIP/2.0", headers, b"payload", packet_id=4
        )

    assert client.dialog_state == "confirmed"
    assert client.last_info_body == "payload"
    assert client.last_notify_event == "door"
    assert client.last_refer_to == "sip:other@example.com"
    assert any(item[0] == "sip_request_received" for item in events)
    assert client._async_send_response.await_args_list[-1].args[1:3] == (501, "Not Implemented")


@pytest.mark.asyncio
async def test_sip_reader_loop_dispatches_responses_and_disconnects(sip):
    client = _client(sip)
    writer = Writer()
    session = sip.SipSession(SimpleNamespace(), writer, "i", "c", "p", "u")
    client._session = session
    client.registered = True
    future = asyncio.get_running_loop().create_future()
    client._pending[("call-1", "MESSAGE")] = future
    frames = [
        b"SIP/2.0 180 Ringing\r\nCall-ID: call-1\r\nCSeq: 1 MESSAGE\r\nContent-Length: 0\r\n\r\n",
        b"SIP/2.0 200 OK\r\nCall-ID: call-1\r\nCSeq: 1 MESSAGE\r\nContent-Length: 0\r\n\r\n",
    ]

    async def read_frame(reader, timeout):  # noqa: ASYNC109 - Preserve the SIP timeout contract (including test doubles).
        if frames:
            return frames.pop(0)
        raise sip.BticinoSipConnectionError("closed")

    client._read_sip_frame = read_frame
    events = []
    client.add_listener(lambda event, data: events.append(event))
    await client._async_reader_loop(session)
    assert future.result()[1] == "SIP/2.0 200 OK"
    assert client.sip_packet_count == 2
    assert client.registered is False
    assert "disconnected" in events


class Response:
    def __init__(self, status=200, text="{}", raw=b"", headers=None):
        self.status = status
        self._text = text
        self._raw = raw
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def text(self):
        return self._text

    async def read(self):
        return self._raw


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def cloud():
    previous = {
        name: module
        for name, module in sys.modules.items()
        if name.startswith("custom_components.btdoor_security_plus")
    }
    _reset_package()
    loaded = _load("cloud")
    try:
        yield loaded
    finally:
        for name in list(sys.modules):
            if name.startswith("custom_components.btdoor_security_plus"):
                sys.modules.pop(name, None)
        sys.modules.update(previous)


@pytest.mark.asyncio
async def test_cloud_request_success_auth_and_http_errors(cloud):
    session = Session([Response(200, '{"ok":true}', headers={"auth_token": "new"})])
    client = cloud.BticinoCloudClient(session, email=" a@b.c ", password="p", base_url="https://x/")
    client.auth_token = "old"
    body, headers = await client._request("POST", "/path", {"a": 1})
    assert body == {"ok": True} and client.auth_token == "new"
    assert session.calls[0][2]["data"] == '{"a":1}'

    with pytest.raises(cloud.BticinoCloudAuthenticationError):
        await cloud.BticinoCloudClient(Session([]), email="a", password="p")._request("GET", "/x")

    client = cloud.BticinoCloudClient(Session([Response(401, "denied")]), email="a", password="p")
    client.auth_token = "t"
    with pytest.raises(cloud.BticinoCloudAuthenticationError):
        await client._request("GET", "/x")

    client = cloud.BticinoCloudClient(Session([Response(500, "boom")]), email="a", password="p")
    client.auth_token = "t"
    with pytest.raises(cloud.BticinoCloudError, match="HTTP 500"):
        await client._request("GET", "/x")


@pytest.mark.asyncio
async def test_cloud_request_bytes_retry_and_errors(cloud, monkeypatch):
    client = cloud.BticinoCloudClient(Session([]), email="a", password="p")
    with pytest.raises(cloud.BticinoCloudAuthenticationError):
        await client._request_bytes("GET", "/x")

    session = Session(
        [OSError("one"), OSError("two"), Response(200, raw=b"cert", headers={"auth_token": "n"})]
    )
    client = cloud.BticinoCloudClient(session, email="a", password="p")
    client.auth_token = "t"
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    raw, _ = await client._request_bytes("POST", "/x", {"a": 1})
    assert raw == b"cert" and client.auth_token == "n"

    client = cloud.BticinoCloudClient(Session([Response(403, raw=b"no")]), email="a", password="p")
    client.auth_token = "t"
    with pytest.raises(cloud.BticinoCloudAuthenticationError):
        await client._request_bytes("GET", "/x")

    client = cloud.BticinoCloudClient(Session([Response(500, raw=b"bad")]), email="a", password="p")
    client.auth_token = "t"
    with pytest.raises(cloud.BticinoCloudError, match="HTTP 500"):
        await client._request_bytes("GET", "/x")
