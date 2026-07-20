"""Central platform runtime orchestration."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from .lifecycle import LifecycleState

AsyncHook = Callable[[], Awaitable[None]]


@dataclass(slots=True)
class BTDoorPlatformRuntime:
    """Coordinate the lifecycle of platform subsystems.

    Subsystems are intentionally registered through hooks so the core remains
    independent from concrete BTicino, Legrand, or Netatmo implementations.
    """

    state: LifecycleState = LifecycleState.CREATED
    _start_hooks: list[AsyncHook] = field(default_factory=list)
    _stop_hooks: list[AsyncHook] = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    metadata: dict[str, Any] = field(default_factory=dict)

    def register(self, *, start: AsyncHook, stop: AsyncHook) -> None:
        """Register a subsystem lifecycle pair."""
        if self.state is not LifecycleState.CREATED:
            raise RuntimeError("Subsystems can only be registered before startup")
        self._start_hooks.append(start)
        self._stop_hooks.insert(0, stop)

    async def async_start(self) -> None:
        """Start all registered subsystems in registration order."""
        async with self._lock:
            if self.state is LifecycleState.RUNNING:
                return
            if self.state not in {LifecycleState.CREATED, LifecycleState.STOPPED}:
                raise RuntimeError(f"Cannot start runtime from {self.state}")
            self.state = LifecycleState.STARTING
            started = 0
            try:
                for hook in self._start_hooks:
                    await hook()
                    started += 1
            except Exception:
                self.state = LifecycleState.FAILED
                for hook in self._stop_hooks[-started:]:
                    try:
                        await hook()
                    except Exception:
                        pass
                raise
            self.state = LifecycleState.RUNNING

    async def async_stop(self) -> None:
        """Stop all registered subsystems in reverse registration order."""
        async with self._lock:
            if self.state in {LifecycleState.CREATED, LifecycleState.STOPPED}:
                self.state = LifecycleState.STOPPED
                return
            self.state = LifecycleState.STOPPING
            errors: list[Exception] = []
            for hook in self._stop_hooks:
                try:
                    await hook()
                except Exception as err:  # pragma: no cover - defensive aggregation
                    errors.append(err)
            self.state = LifecycleState.FAILED if errors else LifecycleState.STOPPED
            if errors:
                raise ExceptionGroup("Failed to stop BTDoor subsystems", errors)

    def diagnostics(self) -> dict[str, Any]:
        """Return a serializable runtime snapshot."""
        return {
            "state": self.state,
            "subsystem_count": len(self._start_hooks),
            "metadata": dict(self.metadata),
        }
