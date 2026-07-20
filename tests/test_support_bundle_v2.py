"""Tests for Support Bundle v2 pure aggregation helpers."""
from custom_components.btdoor_security_plus.developer import DeveloperTools


def test_timeline_summary_aggregates_events() -> None:
    events = [
        {"event": "invite", "duration_seconds": 2},
        {"event": "invite", "duration_seconds": 4},
        {"event": "bye"},
    ]
    result = DeveloperTools._timeline_summary(events)
    assert result["event_count"] == 3
    assert result["events_by_type"] == {"invite": 2, "bye": 1}
    assert result["average_duration_seconds"] == 3.0
    assert result["last_event"]["event"] == "bye"
