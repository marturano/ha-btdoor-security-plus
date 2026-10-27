"""Versioned runtime event models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class RuntimeSource(StrEnum):
    """Logical source of a runtime event."""

    INTEGRATION = "integration"
    CLOUD = "cloud"
    SIP = "sip"
    DIALOG = "dialog"
    MEDIA = "media"
    DIAGNOSTICS = "diagnostics"


class RuntimeEventType(StrEnum):
    """Stable event names consumed by internal and external subscribers."""

    INTEGRATION_STARTED = "integration_started"
    INTEGRATION_STOPPED = "integration_stopped"
    SIP_REGISTERED = "sip_registered"
    SIP_UNREGISTERED = "sip_unregistered"
    INVITE_RECEIVED = "invite_received"
    CALL_STARTED = "call_started"
    CALL_ANSWERED = "call_answered"
    CALL_REJECTED = "call_rejected"
    CALL_CANCELLED = "call_cancelled"
    CALL_ENDED = "call_ended"
    MEDIA_PREPARED = "media_prepared"
    MEDIA_OPENED = "media_opened"
    MEDIA_CLOSED = "media_closed"
    MEDIA_FAILED = "media_failed"
    TLS_CONNECTED = "tls_connected"
    TLS_FAILED = "tls_failed"
    CLOUD_CONNECTED = "cloud_connected"
    CLOUD_DISCONNECTED = "cloud_disconnected"
    GATE_OPENED = "gate_opened"
    SUPPORT_BUNDLE_CREATED = "support_bundle_created"
    DOORBELL_PRESSED = "doorbell_pressed"
    REMOTE_SDP_PARSED = "remote_sdp_parsed"
    LOCAL_SDP_CREATED = "local_sdp_created"
    OFFER_CREATED = "offer_created"
    MEDIA_ALLOCATED = "media_allocated"
    MEDIA_RELEASED = "media_released"
    SRTP_SELECTED = "srtp_selected"
    SDP_OFFER_PARSED = "sdp_offer_parsed"
    RUNTIME_EVENT = "runtime_event"


@dataclass(slots=True, frozen=True)
class RuntimeEvent:
    """One immutable, versioned runtime event."""

    event_type: RuntimeEventType
    source: RuntimeSource
    payload: dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        value = asdict(self)
        value["event_type"] = self.event_type.value
        value["source"] = self.source.value
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> RuntimeEvent:
        """Restore a persisted event, tolerating future extra fields."""
        return cls(
            event_type=RuntimeEventType(str(value.get("event_type", "runtime_event"))),
            source=RuntimeSource(str(value.get("source", "integration"))),
            payload=dict(value.get("payload") or {}),
            schema_version=int(value.get("schema_version", 1)),
            event_id=str(value.get("event_id") or uuid4()),
            timestamp=str(value.get("timestamp") or datetime.now(UTC).isoformat()),
        )
