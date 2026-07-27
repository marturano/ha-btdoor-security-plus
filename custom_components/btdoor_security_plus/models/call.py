"""Immutable call models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CallSnapshot:
    """Read-only current or last-call state."""

    state: str = "idle"
    caller: str | None = None
    caller_uri: str | None = None
    call_id: str | None = None
    started_at: str | None = None
    ended_at: str | None = None
    duration_seconds: float | None = None
    close_reason: str | None = None
    missed: bool = False
