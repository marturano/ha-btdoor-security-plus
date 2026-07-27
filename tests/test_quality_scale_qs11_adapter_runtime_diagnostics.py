"""QS-11 behavioural coverage for adapters, runtime API and diagnostics."""
from __future__ import annotations

import importlib.util
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _reset() -> None:
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus"):
            sys.modules.pop(name, None)
    root = types.ModuleType("custom_components"); root.__path__ = [str(ROOT / "custom_components")]
    pkg = types.ModuleType("custom_components.btdoor_security_plus"); pkg.__path__ = [str(PKG)]
    sys.modules[root.__name__] = root; sys.modules[pkg.__name__] = pkg


def _load(name: str):
    full = f"custom_components.btdoor_security_plus.{name}"
    path = PKG.joinpath(*name.split("."))
    if path.is_dir():
        path = path / "__init__.py"
    else:
        path = path.with_suffix(".py")
    spec = importlib.util.spec_from_file_location(full, path, submodule_search_locations=[str(path.parent)] if path.name == "__init__.py" else None)
    mod = importlib.util.module_from_spec(spec); sys.modules[full] = mod
    assert spec.loader; spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def modules():
    previous = {name: module for name, module in sys.modules.items() if name.startswith("custom_components.btdoor_security_plus")}
    _reset()
    _load("runtime_state.models")
    loaded = SimpleNamespace(
        adapter=_load("adapters.base"),
        provider=_load("runtime_state.provider"),
        api=_load("runtime_state.api"),
        models=sys.modules["custom_components.btdoor_security_plus.runtime_state.models"],
        diag_models=_load("diagnostic_framework.models"),
        diag_provider=_load("diagnostic_framework.providers.test_result"),
        bundle=_load("diagnostic_framework.bundle"),
    )
    try:
        yield loaded
    finally:
        for name in list(sys.modules):
            if name.startswith("custom_components.btdoor_security_plus"):
                sys.modules.pop(name, None)
        sys.modules.update(previous)


@pytest.mark.asyncio
async def test_adapter_defaults_and_capabilities(modules):
    a = modules.adapter
    caps = a.DeviceCapabilities(answer=True, unlock=True)
    assert caps.answer and caps.unlock and not caps.stream

    class Demo(a.DeviceAdapter):
        @property
        def capabilities(self): return caps
        async def async_connect(self): return None
        async def async_disconnect(self): return None
        def diagnostics(self): return {"ok": True}

    obj = Demo()
    assert obj.diagnostics() == {"ok": True}
    for method in (obj.async_answer, obj.async_reject, obj.async_unlock, obj.async_aux, obj.async_snapshot, obj.async_stream):
        with pytest.raises(NotImplementedError):
            await method()


def _runtime(tmp_path: Path):
    cert = tmp_path / "cert.pem"; key = tmp_path / "key.pem"
    cert.write_text("cert"); key.write_text("key")
    client = SimpleNamespace(
        registered=True, last_status="200 OK", dialog_state="confirmed", call_state="active",
        last_sip_method="INVITE", last_call_id="abc", media_runtime_state="active",
        selected_audio_codec="PCMA", selected_video_codec="H264", selected_srtp_suite="AES",
        cloud_last_request_at=datetime(2026, 1, 1, tzinfo=timezone.utc), cloud_last_response_at="done",
        last_completed_media_session={"plan": {"audio": {"remote": {"ip": "10.0.0.2", "port": "4000"}}, "video": {"remote_port": "bad"}}, "srtp_suites": ["AES"], "duration_seconds": "2.5"},
        media_session_history=[1, 2],
    )
    entry = SimpleNamespace(data={"gateway_id": "g1", "gateway_name": "Gate", "client_cert_path": str(cert), "client_key_path": str(key), "port": "5061", "sip_account": "100", "server": "sip.local"})
    runtime = SimpleNamespace(client=client, last_open=datetime(2026, 1, 2, tzinfo=timezone.utc), last_result="ok")
    return entry, runtime


def test_runtime_provider_complete_snapshot(modules, tmp_path):
    entry, runtime = _runtime(tmp_path)
    p = modules.provider.RuntimeStateProvider(entry, runtime)
    assert p.client is runtime.client
    assert p.gateway().gateway_id == "g1"
    assert p.cloud().connected is True
    assert p.sip().port == 5061
    assert p.dialog().call_id == "abc"
    media = p.media(); assert media.remote_audio_port == 4000 and media.remote_video_port is None
    assert media.duration_seconds == 2.5 and media.retained_sessions == 2
    assert p.diagnostics().status == "healthy"
    assert set(p.devices()) == {"gateway", "cloud", "sip", "dialog", "media", "diagnostics"}
    assert p.snapshot().sip.registered is True


def test_runtime_provider_error_paths(modules, tmp_path):
    entry, runtime = _runtime(tmp_path)
    entry.data["port"] = "bad"; entry.data["client_cert_path"] = str(tmp_path / "missing")
    runtime.client.registered = False; runtime.client.last_error = "boom"; runtime.client.cloud_last_error = "auth"
    runtime.client.media_runtime_state = "failed"; runtime.client.last_completed_media_session = {"duration_seconds": "bad"}
    p = modules.provider.RuntimeStateProvider(entry, runtime)
    assert p.cloud().status == "error" and not p.cloud().connected
    assert p.sip().port is None
    assert p.media().duration_seconds is None
    d = p.diagnostics(); assert d.status == "unhealthy" and d.score == 0


@pytest.mark.asyncio
async def test_runtime_api_bundle(modules, tmp_path):
    entry, runtime = _runtime(tmp_path)
    api = modules.api.BTDoorRuntimeAPI(entry, runtime)
    with pytest.raises(RuntimeError):
        await api.async_generate_support_bundle()
    runtime.developer = SimpleNamespace(async_generate_support_report=AsyncMock(return_value={"bundle_path": tmp_path / "bundle.zip"}))
    result = await api.async_generate_support_bundle(include_logs=False)
    assert result == tmp_path / "bundle.zip"
    runtime.developer.async_generate_support_report.assert_awaited_once_with(include_logs=False)


@pytest.mark.asyncio
async def test_diagnostic_result_providers_and_bundle(modules):
    p = modules.diag_provider
    async def collect(): return {"healthy": False, "score": 65, "issues": ["x"]}
    result = await p.TestResultProvider("live", 4, collect).async_collect()
    assert not result.healthy and result.severity == "critical" and result.issues == ["x"]
    result2 = await p.StaticResultProvider("static", 2, {"ok": True, "score": 75, "extra": 1}).async_collect()
    assert result2.healthy and result2.severity == "warning" and "ok" not in result2.details
    payloads = modules.bundle.BundleLayoutBuilder.provider_payloads({"live": result, "static": result2})
    assert set(payloads) == {"diagnostics/providers/live.json", "diagnostics/providers/static.json"}
