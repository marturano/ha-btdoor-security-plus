"""Immutable media models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MediaSnapshot:
    """Read-only media state consumed by diagnostics and UI."""

    state: str = "idle"
    ready: bool = False
    audio_codec: str | None = None
    video_codec: str | None = None
    srtp_suite: str | None = None
    duration_seconds: float | None = None
    close_reason: str | None = None
