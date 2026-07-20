"""Tests for the versioned runtime event model and mapper."""

from custom_components.btdoor_security_plus.event_bus.events import (
    RuntimeEvent,
    RuntimeEventType,
    RuntimeSource,
)
from custom_components.btdoor_security_plus.event_bus.mapper import map_client_event


def test_runtime_event_roundtrip() -> None:
    event = RuntimeEvent(
        event_type=RuntimeEventType.MEDIA_CLOSED,
        source=RuntimeSource.MEDIA,
        payload={"call_id": "abc", "reason": "cancel"},
    )
    restored = RuntimeEvent.from_dict(event.as_dict())
    assert restored == event
    assert restored.schema_version == 1


def test_legacy_media_close_mapping() -> None:
    event = map_client_event(
        "media_session_closed",
        {"call_id": "abc", "closed_reason": "cancel"},
    )
    assert event.event_type is RuntimeEventType.MEDIA_CLOSED
    assert event.source is RuntimeSource.MEDIA
    assert event.payload["legacy_event_type"] == "media_session_closed"


def test_unknown_event_is_retained() -> None:
    event = map_client_event("future_event", {"value": 1})
    assert event.event_type is RuntimeEventType.RUNTIME_EVENT
    assert event.payload == {"legacy_event_type": "future_event", "value": 1}
