"""QS-6 behavioural coverage for developer tooling and lifecycle helpers."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import types
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _module(name: str, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    sys.modules[name] = mod
    return mod


def _load_developer(tmp_path: Path):
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus") or name.startswith(
            "homeassistant"
        ):
            sys.modules.pop(name, None)
    root = _module("custom_components")
    root.__path__ = [str(ROOT / "custom_components")]
    package = _module("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG)]

    _module("homeassistant")
    _module("homeassistant.core", HomeAssistant=object)
    _module(
        "homeassistant.loader", async_get_integration=lambda hass: SimpleNamespace(version="1.2.3")
    )
    _module("homeassistant.helpers")
    _module("homeassistant.helpers.aiohttp_client", async_get_clientsession=lambda hass: "session")
    _module("homeassistant.helpers.entity_registry", async_get=lambda hass: hass.entity_registry)

    _module(
        "custom_components.btdoor_security_plus.const",
        CONF_CLIENT_CERT_PATH="client_cert_path",
        CONF_CLIENT_KEY_PATH="client_key_path",
        CONF_EMAIL="email",
        CONF_GATEWAY_ID="gateway_id",
        CONF_PASSWORD="password",
        CONF_SERVER="server",
        CONF_VERIFY_SERVER="verify_server",
        DOMAIN="btdoor_security_plus",
        SUPPORT_REPORT_RETENTION=2,
    )
    _module(
        "custom_components.btdoor_security_plus.cloud",
        BticinoCloudClient=object,
    )
    _module(
        "custom_components.btdoor_security_plus.support_debug",
        redact=lambda value: value,
        redact_text=lambda value: f"redacted:{value}" if value else value,
        redact_support_text=lambda value: f"safe:{value}",
    )

    class Result:
        def __init__(self, payload):
            self.payload = payload

        def as_dict(self):
            return self.payload

    class Engine:
        def __init__(self, *a, **k):
            pass

    _module(
        "custom_components.btdoor_security_plus.diagnostic_framework",
        DiagnosticEngine=Engine,
        HealthEngine=Engine,
    )
    _module(
        "custom_components.btdoor_security_plus.diagnostic_framework.bundle",
        BundleLayoutBuilder=object,
    )
    _module(
        "custom_components.btdoor_security_plus.diagnostic_framework.providers",
        StaticResultProvider=object,
    )
    _module(
        "custom_components.btdoor_security_plus.support_naming",
        build_support_artifact_names=lambda dt: SimpleNamespace(
            report_name="support.md", bundle_name="support.zip"
        ),
        is_managed_support_artifact=lambda path: path.suffix in {".md", ".zip"},
    )
    _module(
        "custom_components.btdoor_security_plus.visibility",
        visibility_for_entry=lambda entry: SimpleNamespace(as_dict=lambda: {"mode": "all"}),
    )
    _module(
        "custom_components.btdoor_security_plus.support_models",
        SupportSnapshot=dict,
        build_timeline_summary=lambda events: {"count": len(events)},
        json_dumps=lambda value: json.dumps(value, default=str),
        sanitize_jsonl=lambda value: value.replace("secret", "safe"),
        sanitize_support_data=lambda value: value,
        structure_dialog_headers=lambda value: value,
    )

    name = "custom_components.btdoor_security_plus.developer"
    spec = importlib.util.spec_from_file_location(name, PKG / "developer.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def _client():
    now = datetime.now(UTC)
    return SimpleNamespace(
        registered=True,
        last_status="200 OK",
        last_error=None,
        reconnect_count=1,
        dialog_state="confirmed",
        last_sip_method="INVITE",
        last_command_duration=0.1,
        call_state="active",
        call_count=2,
        missed_call_count=1,
        message_count=3,
        connected_at=now,
        last_keepalive_at=now,
        last_call_id="call",
        ringing=True,
        runtime_session_id="session",
        runtime_session_started_at=now,
        media_runtime={
            "state": "prepared",
            "ready_for_answer": True,
            "plan": {
                "audio": {"codec": "PCMU"},
                "video": {"codec": "H264"},
                "srtp": {"suite": "AES"},
            },
        },
        media_plan={"state": "prepared"},
        last_completed_media_session={"state": "closed"},
        media_session_history=[{"duration_seconds": 1}],
        media_session_metrics={"retained_sessions": 1},
        media_instrumentation={"trace": 1},
        sip_dispatcher_diagnostics={"packet_count": 1},
        last_media_remote_sdp="remote",
        last_media_local_sdp="local",
        last_media_sdp_diff="diff",
        last_sdp_offer="v=0",
        last_sdp_summary="summary",
        sdp_session_address="10.0.0.1",
        sdp_audio_address="10.0.0.2",
        sdp_audio_port=4000,
        sdp_audio_protocol="RTP/SAVP",
        sdp_audio_direction="sendrecv",
        sdp_audio_payload_types=(0,),
        sdp_audio_codecs=("PCMU",),
        sdp_audio_fmtp={},
        sdp_video_address="10.0.0.3",
        sdp_video_port=5000,
        sdp_video_protocol="RTP/SAVP",
        sdp_video_direction="recvonly",
        sdp_video_payload_types=(96,),
        sdp_video_codecs=("H264",),
        sdp_video_fmtp={},
        last_dialog_headers={"via": ["x"]},
        sip_timeline=[{"event": "old"}],
        current_session_timeline=[{"event": "new"}],
        _message_challenge="challenge",
        _session=SimpleNamespace(
            identity_uri="sip:user@example",
            contact_uri="sip:user@host",
            proxy_uri="sip:proxy",
            writer=SimpleNamespace(is_closing=lambda: False),
        ),
        client_cert_path="",
        client_key_path="",
        server="sip.example",
        port=5061,
        verify_server=True,
    )


def _tools(module, tmp_path: Path, enabled=True):
    client = _client()
    debug = SimpleNamespace(
        dropped_records=0,
        record=lambda *a, **k: None,
        async_clear=lambda: asyncio.sleep(0),
        log_path=tmp_path / "debug.jsonl",
    )
    runtime = SimpleNamespace(
        client=client, debug=debug, event_bus=None, runtime_events=[], call_journal=[]
    )
    config = SimpleNamespace(
        config_dir=str(tmp_path), path=lambda *parts: str(tmp_path.joinpath(*parts))
    )
    hass = SimpleNamespace(config=config, entity_registry=SimpleNamespace(entities={}))
    entry = SimpleNamespace(
        entry_id="entry", data={"email": "a", "password": "b", "gateway_id": "gw"}, options={}
    )
    return module.DeveloperTools(hass, entry, runtime, enabled), client


def test_developer_enablement_runner_and_basic_tests(tmp_path, monkeypatch):
    module = _load_developer(tmp_path)
    disabled, _ = _tools(module, tmp_path, False)
    with pytest.raises(module.DeveloperModeDisabledError):
        disabled.require_enabled()

    tools, client = _tools(module, tmp_path)
    tools.require_enabled()
    monkeypatch.setattr(tools, "_test_cloud", lambda: asyncio.sleep(0, result={"cloud": True}))

    async def fail():
        raise RuntimeError("secret failure")

    monkeypatch.setattr(tools, "_test_sip", fail)
    result = asyncio.run(tools.async_run_tests("cloud"))
    assert result["cloud"]["ok"] is True
    unknown = asyncio.run(tools.async_run_tests("missing"))
    assert unknown["missing"]["ok"] is False
    failed = asyncio.run(tools.async_run_tests("sip"))
    assert failed["sip"]["ok"] is False and "redacted" in failed["sip"]["error"]

    sdp = asyncio.run(tools._test_sdp())
    assert sdp["available"] and sdp["audio"]["port"] == 4000
    media = asyncio.run(tools._test_media())
    assert media["available"] and media["metrics"]["retained_sessions"] == 1
    dialog = asyncio.run(tools._test_dialog())
    assert dialog["registered"] and dialog["digest_cached"]


def test_developer_certificate_health_files_and_retention(tmp_path, monkeypatch):
    module = _load_developer(tmp_path)
    tools, client = _tools(module, tmp_path)
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    cert.write_text("cert")
    key.write_text("key")
    client.client_cert_path = str(cert)
    client.client_key_path = str(key)
    assert tools._runtime_certificate_paths() == (cert, key)
    status = asyncio.run(tools._certificate_status())
    assert status["certificate_exists"] and status["private_key_exists"]

    health = asyncio.run(tools._test_health())
    assert health["status"] == "healthy" and health["score"] == 100
    client.registered = False
    client._session = None
    unhealthy = asyncio.run(tools._test_health())
    assert unhealthy["status"] in {"degraded", "unhealthy"}

    assert tools._directory_writable(tmp_path / "writable") is True
    blocked = tmp_path / "file"
    blocked.write_text("x")
    assert tools._directory_writable(blocked / "child") is False

    tools.output_dir.mkdir(parents=True, exist_ok=True)
    (tools.output_dir / "a.txt").write_text("x")
    (tools.output_dir / "dir").mkdir()
    assert tools._clear_support_files() == 2

    for stem in ["new", "mid", "old"]:
        (tools.output_dir / f"{stem}.md").write_text(stem)
        (tools.output_dir / f"{stem}.zip").write_text(stem)
    for idx, stem in enumerate(["old", "mid", "new"]):
        ts = 100 + idx
        for suffix in [".md", ".zip"]:
            (tools.output_dir / f"{stem}{suffix}").touch()
            import os

            os.utime(tools.output_dir / f"{stem}{suffix}", (ts, ts))
    tools._enforce_report_retention()
    assert not (tools.output_dir / "old.md").exists()


def test_developer_markdown_bundle_and_cleanup(tmp_path):
    module = _load_developer(tmp_path)
    tools, client = _tools(module, tmp_path)
    snapshot = {
        "generated_at": "now",
        "integration": {"version": "1.0"},
        "system": {"python": "3.13 test", "platform": "linux"},
        "tests": {"sip": {"ok": True, "duration_ms": 1}},
        "health": {"score": 100, "status": "healthy"},
        "runtime": {"media_runtime": client.media_runtime},
    }
    md = tools._markdown(snapshot)
    assert "Report di Supporto" in md and "Media Engine" in md
    assert tools._build_info(snapshot)["version"] == "1.0"
    assert tools._timeline_summary([{"x": 1}]) == {"count": 1}

    tools.output_dir.mkdir(parents=True, exist_ok=True)
    report = tools.output_dir / "report.md"
    report.write_text(md)
    bundle = tools.output_dir / "bundle.zip"
    client.last_completed_media_session = {"state": "closed"}
    tools._write_bundle(
        bundle, report, snapshot, True, {"devices": []}, {"translations": []}, {"entities": []}
    )
    with zipfile.ZipFile(bundle) as zf:
        names = set(zf.namelist())
        assert "support_summary.json" in names and "runtime/runtime.json" in names
        assert "media/remote_sdp.txt" in names

    (tools.output_dir / "other.txt").write_text("x")
    result = asyncio.run(tools.async_clean_debug_environment())
    assert result["removed_files"] >= 2
    assert tools.runtime.last_support_report_path is None
