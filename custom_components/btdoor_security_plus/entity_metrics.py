"""Pure helpers used by Home Assistant status entities."""
from __future__ import annotations

from typing import Any


def last_completed_session(client: Any) -> dict[str, Any]:
    """Return an export-safe last completed media session."""
    value = getattr(client, "last_completed_media_session", None)
    return dict(value) if isinstance(value, dict) else {}


def runtime_health(client: Any) -> tuple[str, int, dict[str, Any]]:
    """Calculate a stable, synchronous runtime health summary."""
    registered = bool(getattr(client, "registered", False))
    last_error = getattr(client, "last_error", None)
    media_state = str(getattr(client, "media_runtime_state", "idle") or "idle")
    dialog_state = str(getattr(client, "dialog_state", "idle") or "idle")

    score = 100
    issues: list[str] = []
    if not registered:
        score -= 50
        issues.append("sip_not_registered")
    if last_error:
        score -= 25
        issues.append("last_error_present")
    if media_state == "failed":
        score -= 25
        issues.append("media_failed")

    score = max(0, score)
    status = "healthy" if score >= 90 else "degraded" if score >= 60 else "unhealthy"
    return status, score, {
        "registered": registered,
        "dialog_state": dialog_state,
        "media_state": media_state,
        "last_error": last_error,
        "issues": issues,
    }


def last_call_summary(client: Any) -> tuple[str | None, dict[str, Any]]:
    """Build a compact state and structured attributes for the last call."""
    session = last_completed_session(client)
    call_state = getattr(client, "call_state", None)
    close_reason = session.get("closed_reason") or call_state
    caller = getattr(client, "last_caller", None)

    state_map = {
        "cancel": "missed",
        "missed": "missed",
        "rejected": "rejected",
        "bye": "completed",
        "completed": "completed",
        "answered": "answered",
    }
    state = state_map.get(str(close_reason).lower(), str(call_state or close_reason or "unknown").lower())

    plan = session.get("plan") if isinstance(session.get("plan"), dict) else {}
    audio = plan.get("audio") if isinstance(plan.get("audio"), dict) else {}
    video = plan.get("video") if isinstance(plan.get("video"), dict) else {}
    attributes = {
        "caller": caller,
        "call_id": session.get("call_id") or getattr(client, "last_call_id", None),
        "duration_seconds": session.get("duration_seconds") or getattr(client, "last_call_duration", None),
        "close_reason": close_reason,
        "audio_codec": audio.get("codec"),
        "video_codec": video.get("codec"),
        "started_at": session.get("started_at") or getattr(client, "call_started_at", None),
        "closed_at": session.get("closed_at") or getattr(client, "call_ended_at", None),
    }
    return state, {key: value for key, value in attributes.items() if value is not None}
