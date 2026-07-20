"""Map legacy client notifications to stable runtime events."""

from __future__ import annotations

from typing import Any

from .events import RuntimeEvent, RuntimeEventType, RuntimeSource

_EVENT_MAP: dict[str, tuple[RuntimeEventType, RuntimeSource]] = {
    "registered": (RuntimeEventType.SIP_REGISTERED, RuntimeSource.SIP),
    "unregistered": (RuntimeEventType.SIP_UNREGISTERED, RuntimeSource.SIP),
    "disconnected": (RuntimeEventType.SIP_UNREGISTERED, RuntimeSource.SIP),
    "connection_restored": (RuntimeEventType.SIP_REGISTERED, RuntimeSource.SIP),
    "invite_received": (RuntimeEventType.INVITE_RECEIVED, RuntimeSource.SIP),
    "call_started": (RuntimeEventType.CALL_STARTED, RuntimeSource.DIALOG),
    "incoming_call": (RuntimeEventType.CALL_STARTED, RuntimeSource.DIALOG),
    "doorbell_pressed": (RuntimeEventType.DOORBELL_PRESSED, RuntimeSource.DIALOG),
    "call_answered": (RuntimeEventType.CALL_ANSWERED, RuntimeSource.DIALOG),
    "call_rejected": (RuntimeEventType.CALL_REJECTED, RuntimeSource.DIALOG),
    "call_cancelled": (RuntimeEventType.CALL_CANCELLED, RuntimeSource.DIALOG),
    "call_ended": (RuntimeEventType.CALL_ENDED, RuntimeSource.DIALOG),
    "missed_call": (RuntimeEventType.CALL_CANCELLED, RuntimeSource.DIALOG),
    "call_timeout": (RuntimeEventType.CALL_ENDED, RuntimeSource.DIALOG),
    "media_remote_sdp_parsed": (RuntimeEventType.REMOTE_SDP_PARSED, RuntimeSource.MEDIA),
    "remote_sdp_parsed": (RuntimeEventType.REMOTE_SDP_PARSED, RuntimeSource.MEDIA),
    "media_local_sdp_created": (RuntimeEventType.LOCAL_SDP_CREATED, RuntimeSource.MEDIA),
    "media_local_sdp_generated": (RuntimeEventType.LOCAL_SDP_CREATED, RuntimeSource.MEDIA),
    "local_sdp_created": (RuntimeEventType.LOCAL_SDP_CREATED, RuntimeSource.MEDIA),
    "media_srtp_selected": (RuntimeEventType.SRTP_SELECTED, RuntimeSource.MEDIA),
    "srtp_selected": (RuntimeEventType.SRTP_SELECTED, RuntimeSource.MEDIA),
    "sdp_offer_parsed": (RuntimeEventType.SDP_OFFER_PARSED, RuntimeSource.MEDIA),
    "media_offer_created": (RuntimeEventType.OFFER_CREATED, RuntimeSource.MEDIA),
    "offer_created": (RuntimeEventType.OFFER_CREATED, RuntimeSource.MEDIA),
    "media_session_allocated": (RuntimeEventType.MEDIA_ALLOCATED, RuntimeSource.MEDIA),
    "media_allocated": (RuntimeEventType.MEDIA_ALLOCATED, RuntimeSource.MEDIA),
    "media_session_released": (RuntimeEventType.MEDIA_RELEASED, RuntimeSource.MEDIA),
    "media_released": (RuntimeEventType.MEDIA_RELEASED, RuntimeSource.MEDIA),
    "media_prepared": (RuntimeEventType.MEDIA_PREPARED, RuntimeSource.MEDIA),
    "media_session_prepared": (RuntimeEventType.MEDIA_PREPARED, RuntimeSource.MEDIA),
    "media_opened": (RuntimeEventType.MEDIA_OPENED, RuntimeSource.MEDIA),
    "media_session_closed": (RuntimeEventType.MEDIA_CLOSED, RuntimeSource.MEDIA),
    "media_failed": (RuntimeEventType.MEDIA_FAILED, RuntimeSource.MEDIA),
    "media_session_failed": (RuntimeEventType.MEDIA_FAILED, RuntimeSource.MEDIA),
    "tls_connected": (RuntimeEventType.TLS_CONNECTED, RuntimeSource.SIP),
    "tls_failed": (RuntimeEventType.TLS_FAILED, RuntimeSource.SIP),
    "cloud_connected": (RuntimeEventType.CLOUD_CONNECTED, RuntimeSource.CLOUD),
    "cloud_disconnected": (RuntimeEventType.CLOUD_DISCONNECTED, RuntimeSource.CLOUD),
    "gate_opened": (RuntimeEventType.GATE_OPENED, RuntimeSource.INTEGRATION),
}


def map_client_event(event_type: str, data: dict[str, object]) -> RuntimeEvent:
    """Normalize a client event while retaining its original name."""
    mapped_type, source = _EVENT_MAP.get(
        event_type,
        (RuntimeEventType.RUNTIME_EVENT, RuntimeSource.INTEGRATION),
    )
    if event_type == "call_ended" and str(data.get("method", "")).upper() == "CANCEL":
        mapped_type = RuntimeEventType.CALL_CANCELLED
    payload: dict[str, Any] = {"legacy_event_type": event_type, **data}
    return RuntimeEvent(event_type=mapped_type, source=source, payload=payload)
