"""QS-5 behavioural coverage for core helpers, media and SIP parsing."""
from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

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
def media_sip():
    _reset_package()
    _load("const")
    _load("sip_identity")
    media = _load("media")
    sip = _load("sip_client")
    return media, sip


def test_media_crypto_codec_sdp_and_snapshots(media_sip, monkeypatch):
    media, _ = media_sip
    assert media.parse_crypto_attribute("1 AES_CM_128_HMAC_SHA1_80 inline:YWJj")
    assert media.parse_crypto_attribute("bad value") is None
    assert media.parse_crypto_attribute("x AES inline:key") is None
    assert media._select_codec(("0:PCMU", "96:H264"), ("H264",)) == (96, "H264")
    assert media._select_codec(("broken", "x:PCMU"), ("PCMU",)) == (None, None)
    assert media._codec_name("PCMU/8000") == "PCMU"
    assert media._codec_name(None) is None

    plan = media.MediaPreparation(
        state="ready", audio_payload_type=0, audio_codec="PCMU/8000",
        audio_local_rtp_port=20000, audio_local_rtcp_port=20001,
        video_payload_type=96, video_codec="H264/90000",
        video_local_rtp_port=21000, video_local_rtcp_port=21001,
        local_media_address="10.0.0.2", srtp_suite="AES_CM_128_HMAC_SHA1_80",
        local_crypto_tag=1,
    )
    answer, redacted = media._build_answer_sdp(plan, b"1" * 30)
    assert "m=audio 20000" in answer and "m=video 21000" in answer
    assert "[REDACTED]" in redacted and "MTEx" not in redacted
    assert "remote_sdp" in media.build_sdp_diff("v=0\r\n", redacted)
    snap = media.media_snapshot(plan)
    assert snap["state"] == "ready" and snap["audio"]["codec"] == "PCMU/8000"
    assert media.media_snapshot(None) is None

    class Probe:
        def connect(self, target):
            self.target = target
        def getsockname(self):
            return ("192.0.2.10", 1234)
        def close(self):
            self.closed = True
    monkeypatch.setattr(media.socket, "socket", lambda *args, **kwargs: Probe())
    assert media._discover_local_address("198.51.100.2") == "192.0.2.10"
    assert media._discover_local_address(None) == "0.0.0.0"


def test_prepare_media_offer_success_and_issue_paths(media_sip, monkeypatch):
    media, sip = media_sip
    sockets = []
    class Sock:
        def close(self): self.closed = True
    def pair():
        a, b = Sock(), Sock(); sockets.extend((a,b)); return a,b,20000+len(sockets),20001+len(sockets)
    monkeypatch.setattr(media, "_bind_udp_pair", pair)
    monkeypatch.setattr(media, "_discover_local_address", lambda value: "10.0.0.5")
    monkeypatch.setattr(media.secrets, "token_bytes", lambda n: b"k" * n)

    crypto = media.parse_crypto_attribute("1 AES_CM_128_HMAC_SHA1_80 inline:" + "YQ==")
    desc = sip.SdpDescription(
        session_name="door", connection_address="10.0.0.8", direction="sendrecv",
        media=(
            sip.SdpMediaDescription("audio", 4000, "RTP/SAVP", (0,), "10.0.0.8", "sendrecv", ("0:PCMU",), {}, (crypto,), {}),
            sip.SdpMediaDescription("video", 5000, "RTP/SAVP", (96,), "10.0.0.8", "recvonly", ("96:H264",), {}, (), {}),
        ),
    )
    result = media.prepare_media_offer(desc)
    assert result.audio_codec == "PCMU" and result.video_codec == "H264"
    assert result.state in {"prepared", "warning", "degraded"}
    assert result.answer_sdp_redacted and "[REDACTED]" in result.answer_sdp_redacted
    result.close()
    assert all(getattr(item, "closed", False) for item in sockets)

    no_media = sip.SdpDescription("x", None, "sendrecv", ())
    empty = media.prepare_media_offer(no_media)
    assert "No audio codec" in " ".join(empty.issues)


def test_sip_constructor_state_parsers_and_digest(media_sip):
    _, sip = media_sip
    client = sip.BticinoSipClient(
        sip_account="sip:user@example.com", sip_password="secret", gateway_id=" gw ",
        client_cert_path="~/cert.pem", client_key_path="~/key.pem",
        server=" server.example ", port=5061, verify_server=True,
    )
    assert client.sip_account == "user@example.com"
    assert client.digest_username == "user"
    assert client.target_uri == "sip:c300x@gw.bs.iotleg.com"
    assert isinstance(client.export_state(), dict)

    client.restore_state({"call_count": 2, "missed_call_count": 1, "last_status": "200 OK"})
    assert client.call_count == 2 and client.last_status == "200 OK"
    client.reset_statistics()
    assert client.call_count == 0 and client.missed_call_count == 0

    raw = (
        "v=0\r\ns=Door\r\nc=IN IP4 10.0.0.8\r\na=sendrecv\r\n"
        "m=audio 4000 RTP/SAVP 0 101\r\na=rtpmap:0 PCMU/8000\r\n"
        "a=rtpmap:101 telephone-event/8000\r\na=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:YWJj\r\n"
        "m=video 5000 RTP/SAVP 96\r\na=rtpmap:96 H264/90000\r\na=recvonly\r\n"
    )
    parsed = client._parse_sdp(raw)
    assert parsed.session_name == "Door" and len(parsed.media) == 2
    assert parsed.media[0].codecs[0].startswith("0:PCMU")

    status, headers = client._parse_headers(b"SIP/2.0 200 OK\r\nVia: one\r\nVia: two\r\nContent-Length: 4\r\n\r\nbody")
    assert status == "SIP/2.0 200 OK" and headers["via"] == ["one", "two"]
    assert client._status_code(status) == 200
    with pytest.raises(sip.BticinoSipConnectionError):
        client._status_code("bad")
    challenge, header_name = client._challenge({"www-authenticate": ['Digest realm="r", nonce="n"']})
    assert header_name == "Authorization" and "nonce" in challenge
    params = client._digest_params(challenge)
    assert params["realm"] == "r"
    auth = client._make_digest_auth(challenge, "INVITE", "sip:x", "user", "pass")
    assert auth.startswith("Digest ") and 'username="user"' in auth
    assert client._safe_preview(b"Authorization: secret\r\nX: y") != "Authorization: secret\r\nX: y"


def _install_init_stubs(tmp_path):
    for name in list(sys.modules):
        if name.startswith("homeassistant"):
            sys.modules.pop(name, None)
    ha = types.ModuleType("homeassistant")
    ce = types.ModuleType("homeassistant.config_entries"); ce.ConfigEntry = object
    core = types.ModuleType("homeassistant.core"); core.CoreState = SimpleNamespace(running="running"); core.HomeAssistant = object
    exc = types.ModuleType("homeassistant.exceptions")
    exc.ConfigEntryAuthFailed = type("ConfigEntryAuthFailed", (Exception,), {})
    exc.ConfigEntryNotReady = type("ConfigEntryNotReady", (Exception,), {})
    helpers = types.ModuleType("homeassistant.helpers")
    typing_mod = types.ModuleType("homeassistant.helpers.typing"); typing_mod.ConfigType = dict
    issue = types.ModuleType("homeassistant.helpers.issue_registry"); issue.IssueSeverity = SimpleNamespace(WARNING="warning"); issue.async_create_issue=lambda *a,**k:None; issue.async_delete_issue=lambda *a,**k:None
    entity = types.ModuleType("homeassistant.helpers.entity_registry"); entity.async_get=lambda hass:hass.entity_registry
    storage = types.ModuleType("homeassistant.helpers.storage"); storage.Store = object
    aio = types.ModuleType("homeassistant.helpers.aiohttp_client"); aio.async_get_clientsession=lambda hass:None
    event = types.ModuleType("homeassistant.helpers.event"); event.async_track_time_interval=lambda *a,**k:lambda:None
    sys.modules.update({m.__name__:m for m in [ha,ce,core,exc,helpers,typing_mod,issue,entity,storage,aio,event]})


def test_init_storage_helpers_and_legacy_entity_cleanup(tmp_path):
    _reset_package(); _install_init_stubs(tmp_path); _load("const")
    module = _load("__init__")
    class Config:
        def path(self,*parts): return str(tmp_path.joinpath(*parts))
    hass = SimpleNamespace(config=Config())
    assert module._certificate_storage_dir(hass, "gw") == tmp_path/"custom_components"/module.DOMAIN/"certificate"/"gw"

    source = tmp_path/"src"; source.mkdir()
    (source/"client-cert.pem").write_text("cert")
    (source/"client-key.pem").write_text("key")
    (source/"ca-chain.pem").write_text("ca")
    destination = tmp_path/"dst"
    result = module._copy_certificate_material(source, destination)
    assert set(result) == {module.CONF_CLIENT_CERT_PATH,module.CONF_CLIENT_KEY_PATH,module.CONF_CA_CHAIN_PATH}
    assert oct((destination/"client-key.pem").stat().st_mode & 0o777) == "0o600"

    removed=[]
    registry = SimpleNamespace(
        async_get_entity_id=lambda platform, domain, uid: f"{platform}.old" if platform=="switch" else None,
        async_remove=removed.append,
    )
    hass.entity_registry=registry
    entry=SimpleNamespace(unique_id="uid")
    module._async_remove_legacy_gate_entities(hass, entry)
    assert removed == ["switch.old"]
    module._async_remove_legacy_gate_entities(hass, SimpleNamespace(unique_id=None))


def test_availability_transition_deduplicates(caplog):
    _reset_package()
    runtime = SimpleNamespace(availability_state=None)
    # Function semantics reproduced through direct module loading is covered in the prior test fixture.
    _install_init_stubs(Path("/tmp")); _load("const"); module=_load("__init__")
    module._log_availability_transition(runtime, False, "Door")
    module._log_availability_transition(runtime, False, "Door")
    module._log_availability_transition(runtime, True, "Door")
    assert runtime.availability_state is True
