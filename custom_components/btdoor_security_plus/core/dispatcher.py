"""Typed dispatcher facade for BTDoor Security+ runtime events."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from ..event_bus import RuntimeEvent, RuntimeEventBus, RuntimeEventType


class RuntimeEventSubscriber(Protocol):
    """Contract implemented by runtime event subscribers."""

    def __call__(self, event: RuntimeEvent) -> None:
        """Consume one immutable runtime event."""


class RuntimeDispatcher:
    """Expose a narrow event API without leaking Event Bus internals."""

    def __init__(self, event_bus: RuntimeEventBus) -> None:
        self._event_bus = event_bus

    def publish(self, event: RuntimeEvent) -> None:
        """Publish one typed runtime event."""
        self._event_bus.publish(event)

    def subscribe(
        self,
        subscriber: RuntimeEventSubscriber,
        event_type: RuntimeEventType | None = None,
    ) -> Callable[[], None]:
        """Subscribe using the existing Event Bus compatibility contract."""
        return self._event_bus.subscribe(subscriber, event_type)

    @property
    def event_bus(self) -> RuntimeEventBus:
        """Return the underlying bus for temporary 6.0.x adapters."""
        return self._event_bus
