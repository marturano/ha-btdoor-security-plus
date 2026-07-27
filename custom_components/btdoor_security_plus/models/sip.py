"""Immutable SIP models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SipSnapshot:
    """Read-only SIP state consumed by diagnostics and UI."""

    registered: bool = False
    status: str | None = None
    server: str | None = None
    port: int | None = None
    transport: str = "tls"
    dialog_state: str = "idle"
    last_method: str | None = None
    last_response_code: int | None = None
    reconnect_count: int = 0
    last_error: str | None = None
