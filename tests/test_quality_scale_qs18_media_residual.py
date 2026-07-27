"""QS-18 behavioural coverage for residual media and package paths."""
from __future__ import annotations

import base64
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"

def _load_media():
    root = sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
    root.__path__ = [str(ROOT / "custom_components")]
    package = sys.modules.setdefault("custom_components.btdoor_security_plus", types.ModuleType("custom_components.btdoor_security_plus"))
    package.__path__ = [str(PKG)]
    name = "custom_components.btdoor_security_plus.media"
    spec = importlib.util.spec_from_file_location(name, PKG / "media.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module

media = _load_media()


def test_crypto_offer_edge_properties_and_public_export() -> None:
    non_inline = media.SrtpCryptoOffer(1, "AES", "prompt", "secret")
    assert non_inline.inline_value is None
    assert non_inline.decoded_key is None

    invalid = media.SrtpCryptoOffer(2, "AES", "inline", "not-base64|2^20|7:4")
    assert invalid.decoded_key is None
    assert invalid.lifetime == "2^20"
    assert invalid.mki == "7:4"
    exported = invalid.public_dict()
    assert exported["key_length"] is None
    assert exported["mki_present"] is True

    plain = media.SrtpCryptoOffer(3, "AES", "inline", base64.b64encode(b"x" * 30).decode())
    assert plain.lifetime is None
    assert plain.mki is None
    assert plain.public_dict()["key_length"] == 30


def test_media_close_tolerates_socket_errors_and_empty_diff() -> None:
    class BadSocket:
        def close(self) -> None:
            raise OSError("already closed")

    plan = media.MediaPreparation(state="prepared", _sockets=(BadSocket(),), _local_key=b"x")
    plan.close()
    assert plan.state == "released"
    assert plan._sockets == ()
    assert plan._local_key is None
    assert media.build_sdp_diff(None, None) == ""


def test_udp_pair_retries_and_discovery_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    created = []

    class FakeSocket:
        def __init__(self) -> None:
            self.closed = False
            self.bind_calls = 0
            created.append(self)

        def bind(self, _address) -> None:
            self.bind_calls += 1
            raise OSError("busy")

        def setblocking(self, _value) -> None:
            pass

        def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(media.socket, "socket", lambda *_a, **_k: FakeSocket())
    monkeypatch.setattr(media.secrets, "randbelow", lambda _n: 0)
    with pytest.raises(OSError, match="Unable to reserve"):
        media._bind_udp_pair()
    assert created and all(sock.closed for sock in created)

    class Probe:
        def connect(self, _target) -> None:
            raise OSError("route unavailable")

        def close(self) -> None:
            self.closed = True

    probe = Probe()
    monkeypatch.setattr(media.socket, "socket", lambda *_a, **_k: probe)
    assert media._discover_local_address("192.0.2.1") == "0.0.0.0"
    assert probe.closed is True


def test_prepare_media_offer_degraded_and_cleanup(monkeypatch: pytest.MonkeyPatch) -> None:
    class Sock:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    sockets = []

    def pair():
        a, b = Sock(), Sock()
        sockets.extend((a, b))
        return a, b, 22000, 22001

    monkeypatch.setattr(media, "_bind_udp_pair", pair)
    monkeypatch.setattr(media, "_discover_local_address", lambda _address: "10.0.0.2")
    monkeypatch.setattr(media.secrets, "token_bytes", lambda n: b"k" * n)

    bad_crypto = media.SrtpCryptoOffer(1, "AES_CM_128_HMAC_SHA1_80", "inline", "bad")
    audio = SimpleNamespace(
        media="audio", port=4000, codecs=("0:PCMU/8000",), connection_address="10.0.0.8",
        protocol="RTP/SAVP", crypto=(bad_crypto,),
    )
    video = SimpleNamespace(
        media="video", port=5000, codecs=("broken",), connection_address="10.0.0.8",
        protocol="RTP/SAVP", crypto=(),
    )
    result = media.prepare_media_offer(SimpleNamespace(media=(audio, video)))
    assert result.state == "degraded"
    assert any("not valid base64" in issue for issue in result.issues)
    assert any("No video codec" in issue for issue in result.issues)
    result.close()

    cleanup_sockets = []
    calls = 0

    def exploding_pair():
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("boom")
        a, b = Sock(), Sock()
        cleanup_sockets.extend((a, b))
        return a, b, 23000, 23001

    monkeypatch.setattr(media, "_bind_udp_pair", exploding_pair)
    with pytest.raises(RuntimeError, match="boom"):
        media.prepare_media_offer(SimpleNamespace(media=(audio, video)))
    assert cleanup_sockets and all(sock.closed for sock in cleanup_sockets)
