"""Immutable Cloud models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CloudSnapshot:
    """Read-only Cloud state consumed by diagnostics and UI."""

    status: str = "unknown"
    connected: bool = False
    authenticated: bool = False
    gateway_count: int = 0
    configured_gateway_found: bool = False
    endpoint: str | None = None
    last_request: str | None = None
    last_response: str | None = None
    last_error: str | None = None
