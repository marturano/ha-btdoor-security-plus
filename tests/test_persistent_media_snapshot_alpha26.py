"""Regression tests for alpha.26 persistent media snapshots."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from custom_components.btdoor_security_plus.sip_client import BticinoSipClient


def _client_without_init() -> BticinoSipClient:
    client = object.__new__(BticinoSipClient)
    client.media_session_history = __import__("collections").deque(maxlen=10)
    client.last_completed_media_session = None
    client.media_runtime_state = "closed"
    client.media_runtime_call_id = "call-1"
    client.media_runtime_started_at = datetime.now(UTC) - timedelta(seconds=4)
    client.media_runtime_prepared_at = datetime.now(UTC) - timedelta(seconds=3)
    client.media_runtime_closed_at = datetime.now(UTC)
    client.last_media_preparation = {
        "state": "released",
        "audio": {"codec": "SPEEX/8000"},
        "video": {"codec": "H264/90000"},
        "srtp": {"suite": "AES_CM_128_HMAC_SHA1_80"},
        "issues": [],
    }
    client.media_preparation = None
    client.last_media_remote_sdp = "v=0"
    client.last_media_local_sdp = "v=0"
    client.last_media_sdp_diff = ""
    client.media_trace_id = "MT-000001"
    client.media_trace_state = "closed"
    client.media_trace_error = None
    client.media_trace = __import__("collections").deque([{"stage": "prepared"}], maxlen=100)
    return client


def test_media_metrics_aggregate_history() -> None:
    client = _client_without_init()
    client.media_session_history.extend(
        [
            {
                "duration_seconds": 2.0,
                "closed_reason": "cancel",
                "closed_at": "a",
                "plan": {"audio": {"codec": "SPEEX/8000"}},
            },
            {
                "duration_seconds": 4.0,
                "closed_reason": "bye",
                "closed_at": "b",
                "plan": {"audio": {"codec": "SPEEX/8000"}, "video": {"codec": "H264/90000"}},
            },
        ]
    )
    metrics = client.media_session_metrics
    assert metrics["retained_sessions"] == 2
    assert metrics["average_duration_seconds"] == 3.0
    assert metrics["close_reasons"] == {"cancel": 1, "bye": 1}
    assert metrics["codec_usage"]["SPEEX/8000"] == 2


def test_media_diagnostics_exposes_last_completed_and_history() -> None:
    client = _client_without_init()
    client.last_completed_media_session = {"closed_reason": "cancel"}
    client.media_session_history.append(client.last_completed_media_session)
    payload = client.media_diagnostics
    assert payload["last_completed"]["closed_reason"] == "cancel"
    assert len(payload["history"]) == 1
    assert payload["current"]["remote_sdp_available"] is True
