"""Immutable public runtime state models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class GatewayState:
    gateway_id: str | None = None
    gateway_name: str | None = None
    device_name: str | None = None
    plant_id: str | None = None
    plant_name: str | None = None
    last_open: str | None = None
    last_result: str | None = None


@dataclass(frozen=True, slots=True)
class CloudState:
    status: str = "unknown"
    connected: bool = False
    authenticated: bool = False
    endpoint: str | None = None
    last_request: str | None = None
    last_response: str | None = None
    last_error: str | None = None
    certificate_ready: bool = False


@dataclass(frozen=True, slots=True)
class SipState:
    registered: bool = False
    status: str | None = None
    account: str | None = None
    server: str | None = None
    port: int | None = None
    transport: str = "tls"
    dialog_state: str = "idle"
    last_method: str | None = None
    last_call_id: str | None = None
    last_error: str | None = None


@dataclass(frozen=True, slots=True)
class DialogState:
    state: str = "idle"
    call_state: str | None = None
    caller: str | None = None
    caller_uri: str | None = None
    caller_domain: str | None = None
    caller_tag: str | None = None
    last_method: str | None = None
    call_id: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


@dataclass(frozen=True, slots=True)
class MediaState:
    state: str = "idle"
    ready: bool = False
    audio_codec: str | None = None
    video_codec: str | None = None
    remote_audio_ip: str | None = None
    remote_audio_port: int | None = None
    remote_video_ip: str | None = None
    remote_video_port: int | None = None
    srtp_suite: str | None = None
    duration_seconds: float | None = None
    close_reason: str | None = None
    started_at: str | None = None
    closed_at: str | None = None
    retained_sessions: int = 0


@dataclass(frozen=True, slots=True)
class DiagnosticsState:
    status: str = "unknown"
    score: int = 0
    issues: tuple[str, ...] = field(default_factory=tuple)
    sip_registered: bool = False
    dialog_state: str = "idle"
    media_state: str = "idle"
    last_error: str | None = None


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    gateway: GatewayState
    cloud: CloudState
    sip: SipState
    dialog: DialogState
    media: MediaState
    diagnostics: DiagnosticsState

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-safe mapping for diagnostics and support exports."""
        return asdict(self)
