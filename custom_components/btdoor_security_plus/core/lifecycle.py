"""Lifecycle primitives and cleanup tracking for BTDoor Security+."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum


class LifecycleState(StrEnum):
    """Runtime lifecycle state."""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(slots=True)
class LifecycleCleanupRegistry:
    """Track idempotent cleanup callbacks owned by one config entry."""

    _callbacks: list[Callable[[], None]] = field(default_factory=list)

    def add(self, callback: Callable[[], None]) -> None:
        """Register a cleanup callback in creation order."""
        self._callbacks.append(callback)

    def run(self) -> tuple[Exception, ...]:
        """Run callbacks in reverse order and aggregate failures."""
        errors: list[Exception] = []
        while self._callbacks:
            callback = self._callbacks.pop()
            try:
                callback()
            except Exception as err:  # pragma: no cover - defensive aggregation
                errors.append(err)
        return tuple(errors)

    @property
    def pending(self) -> int:
        """Return the number of callbacks not yet executed."""
        return len(self._callbacks)
