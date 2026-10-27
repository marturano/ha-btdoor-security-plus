"""Regression tests for alpha.29 media lifecycle persistence."""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime, timedelta

from custom_components.btdoor_security_plus.sip_client import BticinoSipClient


def _bare_client() -> BticinoSipClient:
    client = BticinoSipClient(
        sip_account="test",
        sip_password="test",
        gateway_id="gateway",
        client_cert_path="cert.pem",
        client_key_path="key.pem",
        server="localhost",
        port=5061,
        verify_server=False,
    )
    client.media_preparation = None
    client.last_media_preparation = {
        "state": "released",
        "audio": {"codec": "SPEEX/8000", "remote_address": "172.211.8.196", "remote_port": 15372},
        "video": {"codec": "H264/90000", "remote_address": "172.211.8.196", "remote_port": 27410},
        "srtp": {"suite": "AES_CM_128_HMAC_SHA1_80"},
        "issues": [],
    }
    client.media_runtime_state = "prepared"
    client.media_runtime_call_id = "call-alpha29"
    client.media_runtime_started_at = datetime.now(UTC) - timedelta(seconds=5)
    client.media_runtime_prepared_at = datetime.now(UTC) - timedelta(seconds=4)
    client.media_runtime_closed_at = None
    client.last_media_remote_sdp = "v=0\r\n"
    client.last_media_local_sdp = "v=0\r\n"
    client.last_media_sdp_diff = ""
    client.media_trace_counter = 1
    client.media_trace_id = "MT-000001"
    client.media_trace_state = "prepared"
    client.media_trace_error = None
    client.media_trace = deque([{"stage": "runtime_updated"}], maxlen=100)
    client.media_session_history = deque(maxlen=10)
    client.last_completed_media_session = None
    client.sip_dispatcher_trace = deque([{"stage": "invite_branch_completed"}], maxlen=250)
    client.sip_packet_count = 2
    client.invite_received_count = 1
    client.invite_dispatched_count = 1
    client.invite_with_sdp_count = 1
    client.invite_media_runtime_count = 1
    client.call_state = "missed"
    client._active_call_id = "call-alpha29"
    client.last_call_id = "call-alpha29"
    client.runtime_session_id = "runtime-alpha29"
    client._listeners = set()
    client._debug = None
    return client


def test_release_persists_completed_snapshot_once() -> None:
    client = _bare_client()
    client._release_media_preparation("cancel")
    assert client.last_completed_media_session is not None
    assert client.last_completed_media_session["closed_reason"] == "cancel"
    assert client.last_completed_media_session["plan"]["audio"]["remote_port"] == 15372
    assert len(client.media_session_history) == 1

    client._release_media_preparation("cancel")
    assert len(client.media_session_history) == 1


def test_export_restore_round_trip_keeps_media_history() -> None:
    source = _bare_client()
    source._release_media_preparation("cancel")
    state = source.export_state()

    restored = _bare_client()
    restored.media_runtime_state = "idle"
    restored.media_session_history.clear()
    restored.last_completed_media_session = None
    restored.restore_state(state)

    assert restored.last_completed_media_session is not None
    assert restored.last_completed_media_session["closed_reason"] == "cancel"
    assert len(restored.media_session_history) == 1
    assert restored.media_session_metrics["close_reasons"] == {"cancel": 1}
    assert restored.sip_packet_count == 2
    assert restored.invite_media_runtime_count == 1
