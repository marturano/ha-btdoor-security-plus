"""Build a provider-neutral operational runtime summary."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeSummary:
    overall_status: str
    health_score: int
    gateway_name: str | None
    cloud_connected: bool
    cloud_status: str
    sip_registered: bool
    sip_status: str | None
    dialog_state: str
    call_state: str | None
    last_caller: str | None
    media_state: str
    media_ready: bool
    audio_codec: str | None
    video_codec: str | None
    srtp_suite: str | None
    last_call_duration_seconds: float | None
    last_call_close_reason: str | None
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_runtime_summary(provider: Any) -> RuntimeSummary:
    snapshot = provider.snapshot()
    return RuntimeSummary(
        overall_status=snapshot.diagnostics.status,
        health_score=snapshot.diagnostics.score,
        gateway_name=snapshot.gateway.gateway_name or snapshot.gateway.device_name,
        cloud_connected=snapshot.cloud.connected,
        cloud_status=snapshot.cloud.status,
        sip_registered=snapshot.sip.registered,
        sip_status=snapshot.sip.status,
        dialog_state=snapshot.dialog.state,
        call_state=snapshot.dialog.call_state,
        last_caller=snapshot.dialog.caller,
        media_state=snapshot.media.state,
        media_ready=snapshot.media.ready,
        audio_codec=snapshot.media.audio_codec,
        video_codec=snapshot.media.video_codec,
        srtp_suite=snapshot.media.srtp_suite,
        last_call_duration_seconds=snapshot.media.duration_seconds,
        last_call_close_reason=snapshot.media.close_reason,
        warnings=snapshot.diagnostics.issues,
    )
