"""Lifecycle primitives for the BTDoor Security+ platform."""

from __future__ import annotations

from enum import StrEnum


class LifecycleState(StrEnum):
    """Runtime lifecycle state."""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
