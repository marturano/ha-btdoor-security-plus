"""Per-config-entry runtime event bus with bounded persistence."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Any

from homeassistant.helpers.storage import Store

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

    async def async_load(self) -> None:
        """Load persisted events without failing integration setup."""
        stored = await self._store.async_load() or {}
        for item in stored.get("events", []):
            try:
                self._events.append(RuntimeEvent.from_dict(dict(item)))
            except (TypeError, ValueError):
                continue

    def publish(self, event: RuntimeEvent) -> None:
        """Publish one event and schedule persistence."""
        self._events.append(event)
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

    @property
    def metrics(self) -> dict[str, Any]:
        """Return compact event counters."""
        counts: dict[str, int] = {}
        sources: dict[str, int] = {}
        for event in self._events:
            counts[event.event_type.value] = counts.get(event.event_type.value, 0) + 1
            sources[event.source.value] = sources.get(event.source.value, 0) + 1
        return {
            "schema_version": 1,
            "retained_events": len(self._events),
            "events_by_type": counts,
            "events_by_source": sources,
            "last_event": self._events[-1].as_dict() if self._events else None,
        }

    def export_state(self) -> dict[str, Any]:
        """Return storage-safe state."""
        return {"schema_version": 1, "events": self.history}
