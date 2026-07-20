"""Regression tests for the Beta.1 runtime-state facade."""
from types import SimpleNamespace

from custom_components.btdoor_security_plus.runtime_state import RuntimeStateProvider


def _provider(tmp_path):
    cert = tmp_path / "client.pem"
    key = tmp_path / "client.key"
    cert.write_text("cert")
    key.write_text("key")
    entry = SimpleNamespace(data={
        "gateway_id": "gw-1",
        "gateway_name": "Gateway",
        "device_name": "C300X",
        "plant_id": "plant-1",
        "plant_name": "Home",
        "sip_account": "ha-user",
        "server": "sip.example.test",
        "port": 5061,
        "client_cert_path": str(cert),
        "client_key_path": str(key),
    })
    client = SimpleNamespace(
        registered=True,
        last_status="registered",
        last_error=None,
        dialog_state="terminated",
        last_sip_method="CANCEL",
        last_call_id="call-1",
        call_state="missed",
        last_caller="c300x",
        last_caller_uri="sip:c300x@example.test",
        last_caller_domain="example.test",
        last_caller_tag="tag-1",
        call_started_at=None,
        call_ended_at=None,
        media_runtime_state="closed",
        selected_audio_codec=None,
        selected_video_codec=None,
        selected_srtp_suite=None,
        last_call_duration=9.5,
        media_session_history=[{"call_id": "call-1"}],
        last_completed_media_session={
            "call_id": "call-1",
            "closed_reason": "cancel",
            "duration_seconds": 9.5,
            "plan": {
                "audio": {"codec": "SPEEX/8000", "remote": {"ip": "192.0.2.10", "port": 12000}},
                "video": {"codec": "H264/90000", "remote": {"ip": "192.0.2.10", "port": 13000}},
                "srtp_suite": "AES_CM_128_HMAC_SHA1_80",
            },
        },
    )
    runtime = SimpleNamespace(client=client, last_open=None, last_result="ok")
    return RuntimeStateProvider(entry, runtime)


def test_snapshot_is_structured_and_immutable(tmp_path):
    provider = _provider(tmp_path)
    snapshot = provider.snapshot()
    assert snapshot.gateway.gateway_id == "gw-1"
    assert snapshot.cloud.certificate_ready is True
    assert snapshot.sip.registered is True
    assert snapshot.dialog.caller == "c300x"
    assert snapshot.media.audio_codec == "SPEEX/8000"
    assert snapshot.media.remote_video_port == 13000
    assert snapshot.diagnostics.score == 100
    assert snapshot.as_dict()["media"]["close_reason"] == "cancel"


def test_health_isolated_from_media_history(tmp_path):
    provider = _provider(tmp_path)
    provider.client.registered = False
    state = provider.diagnostics()
    assert state.status == "unhealthy"
    assert state.score == 50
    assert state.issues == ("sip_not_registered",)
