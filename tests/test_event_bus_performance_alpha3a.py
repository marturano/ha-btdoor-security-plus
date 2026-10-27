"""Regression tests for the alpha.3a Event Bus performance hotfix."""

from unittest.mock import Mock

from custom_components.btdoor_security_plus.event_bus.bus import RuntimeEventBus
from custom_components.btdoor_security_plus.event_bus.events import (
    RuntimeEvent,
    RuntimeEventType,
    RuntimeSource,
)


def test_compact_history_does_not_serialize_payloads() -> None:
    store = Mock()
    store.async_delay_save = Mock()
    bus = RuntimeEventBus(store, max_events=500)
    payload = {"large": "x" * 200_000}
    for _ in range(30):
        bus.publish(
            RuntimeEvent(RuntimeEventType.RUNTIME_EVENT, RuntimeSource.DIAGNOSTICS, payload)
        )

    timeline = bus.compact_history(20)

    assert len(timeline) == 20
    assert all(set(item) == {"timestamp", "type", "source"} for item in timeline)
    assert all("payload" not in item for item in timeline)
    assert bus.retained_count == 30


def test_incremental_metrics_follow_bounded_history() -> None:
    store = Mock()
    store.async_delay_save = Mock()
    bus = RuntimeEventBus(store, max_events=2)
    bus.publish(RuntimeEvent(RuntimeEventType.SIP_REGISTERED, RuntimeSource.SIP))
    bus.publish(RuntimeEvent(RuntimeEventType.GATE_OPENED, RuntimeSource.SIP))
    bus.publish(RuntimeEvent(RuntimeEventType.CLOUD_CONNECTED, RuntimeSource.CLOUD))

    metrics = bus.metrics
    assert metrics["retained_events"] == 2
    assert metrics["events_by_type"] == {"gate_opened": 1, "cloud_connected": 1}
    assert metrics["events_by_source"] == {"sip": 1, "cloud": 1}
