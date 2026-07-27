"""Per-config-entry runtime event bus with bounded persistence."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.helpers.storage import Store
else:
    Store = Any

from .events import RuntimeEvent, RuntimeEventType

RuntimeEventListener = Callable[[RuntimeEvent], None]


class RuntimeEventBus:
    """Publish versioned events and retain a bounded event history."""

    def __init__(
        self,
        store: Store[dict[str, Any]],
        *,
        max_events: int = 500,
    ) -> None:
        self._store = store
        self._events: deque[RuntimeEvent] = deque(maxlen=max_events)
        self._listeners: set[RuntimeEventListener] = set()
        self._typed_listeners: dict[RuntimeEventType, set[RuntimeEventListener]] = {}
        self._counts_by_type: dict[str, int] = {}
        self._counts_by_source: dict[str, int] = {}

    async def async_load(self) -> None:
        """Load persisted events without failing integration setup."""
        stored = await self._store.async_load() or {}
        for item in stored.get("events", []):
            try:
                event = RuntimeEvent.from_dict(dict(item))
                self._events.append(event)
                self._increment_counters(event)
            except (TypeError, ValueError):
                continue

    def publish(self, event: RuntimeEvent) -> None:
        """Publish one event and schedule persistence."""
        if len(self._events) == self._events.maxlen and self._events:
            self._decrement_counters(self._events[0])
        self._events.append(event)
        self._increment_counters(event)
        self._store.async_delay_save(self.export_state, 1.0)
        for listener in tuple(self._listeners):
            listener(event)
        for listener in tuple(self._typed_listeners.get(event.event_type, set())):
            listener(event)

    def subscribe(
        self,
        listener: RuntimeEventListener,
        event_type: RuntimeEventType | None = None,
    ) -> Callable[[], None]:
        """Subscribe to all events or to one event type."""
        listeners = self._listeners if event_type is None else self._typed_listeners.setdefault(event_type, set())
        listeners.add(listener)

        def _remove() -> None:
            listeners.discard(listener)

        return _remove

    @property
    def history(self) -> list[dict[str, Any]]:
        """Return the retained event history."""
        return [event.as_dict() for event in self._events]

    def compact_history(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return lightweight metadata for the most recent events."""
        if limit <= 0:
            return []
        events = list(self._events)[-limit:]
        return [
            {
                "timestamp": event.timestamp,
                "type": event.event_type.value,
                "source": event.source.value,
            }
            for event in events
        ]

    @property
    def retained_count(self) -> int:
        """Return the number of retained events without serializing history."""
        return len(self._events)

    @property
    def last_event_summary(self) -> dict[str, Any] | None:
        """Return lightweight metadata for the last event."""
        if not self._events:
            return None
        event = self._events[-1]
        return {
            "timestamp": event.timestamp,
            "type": event.event_type.value,
            "source": event.source.value,
        }

    @property
    def metrics(self) -> dict[str, Any]:
        """Return compact event counters without rescanning event payloads."""
        return {
            "schema_version": 1,
            "retained_events": len(self._events),
            "events_by_type": dict(self._counts_by_type),
            "events_by_source": dict(self._counts_by_source),
            "last_event": self.last_event_summary,
        }

    def _increment_counters(self, event: RuntimeEvent) -> None:
        event_type = event.event_type.value
        source = event.source.value
        self._counts_by_type[event_type] = self._counts_by_type.get(event_type, 0) + 1
        self._counts_by_source[source] = self._counts_by_source.get(source, 0) + 1

    def _decrement_counters(self, event: RuntimeEvent) -> None:
        event_type = event.event_type.value
        source = event.source.value
        self._counts_by_type[event_type] = max(0, self._counts_by_type.get(event_type, 0) - 1)
        self._counts_by_source[source] = max(0, self._counts_by_source.get(source, 0) - 1)
        if self._counts_by_type[event_type] == 0:
            self._counts_by_type.pop(event_type, None)
        if self._counts_by_source[source] == 0:
            self._counts_by_source.pop(source, None)

    def export_state(self) -> dict[str, Any]:
        """Return storage-safe state."""
        return {"schema_version": 1, "events": self.history}
