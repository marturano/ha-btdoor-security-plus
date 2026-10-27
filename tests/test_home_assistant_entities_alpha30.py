"""Tests for alpha.30 entity helper semantics."""

from types import SimpleNamespace

from custom_components.btdoor_security_plus.entity_metrics import (
    last_call_summary,
    runtime_health,
)


def _client(**kwargs):
    defaults = {
        "registered": True,
        "last_error": None,
        "media_runtime_state": "closed",
        "dialog_state": "terminated",
        "call_state": "missed",
        "last_caller": "c300x",
        "last_call_id": "call-1",
        "last_call_duration": 12.5,
        "call_started_at": None,
        "call_ended_at": None,
        "last_completed_media_session": {
            "call_id": "call-1",
            "closed_reason": "cancel",
            "duration_seconds": 12.5,
            "plan": {
                "audio": {"codec": "SPEEX/8000"},
                "video": {"codec": "H264/90000"},
            },
        },
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_runtime_health_healthy():
    status, score, details = runtime_health(_client())
    assert status == "healthy"
    assert score == 100
    assert details["issues"] == []


def test_runtime_health_detects_registration_failure():
    status, score, details = runtime_health(_client(registered=False))
    assert status == "unhealthy"
    assert score == 50
    assert "sip_not_registered" in details["issues"]


def test_last_call_summary_uses_persistent_media_session():
    state, attrs = last_call_summary(_client())
    assert state == "missed"
    assert attrs["caller"] == "c300x"
    assert attrs["audio_codec"] == "SPEEX/8000"
    assert attrs["video_codec"] == "H264/90000"
    assert attrs["close_reason"] == "cancel"
