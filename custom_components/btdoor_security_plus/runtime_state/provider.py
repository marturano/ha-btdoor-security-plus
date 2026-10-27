"""Single source of truth for immutable BTDoor runtime snapshots."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .models import (
    CloudState,
    DiagnosticsState,
    DialogState,
    GatewayState,
    MediaState,
    RuntimeSnapshot,
    SipState,
)


def _iso(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value) if value not in (None, "") else None


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _endpoint(media: dict[str, Any]) -> tuple[str | None, int | None]:
    remote = _mapping(media.get("remote"))
    ip = remote.get("ip") or media.get("remote_ip") or media.get("address")
    port = remote.get("port") or media.get("remote_port") or media.get("port")
    try:
        parsed_port = int(port) if port is not None else None
    except (TypeError, ValueError):
        parsed_port = None
    return (str(ip) if ip else None, parsed_port)


def _codec(media: dict[str, Any]) -> str | None:
    value = media.get("codec") or media.get("selected_codec")
    return str(value) if value else None


class RuntimeStateProvider:
    """Build stable snapshots without exposing mutable engine internals."""

    def __init__(self, entry: Any, runtime_data: Any) -> None:
        self._entry = entry
        self._runtime = runtime_data

    @property
    def client(self) -> Any:
        return self._runtime.client

    def gateway(self) -> GatewayState:
        data = self._entry.data
        return GatewayState(
            gateway_id=_optional(data.get("gateway_id")),
            gateway_name=_optional(data.get("gateway_name")),
            device_name=_optional(data.get("device_name")),
            plant_id=_optional(data.get("plant_id")),
            plant_name=_optional(data.get("plant_name")),
            last_open=_iso(self._runtime.last_open),
            last_result=_optional(self._runtime.last_result),
        )

    def cloud(self) -> CloudState:
        data = self._entry.data
        cert = Path(str(data.get("client_cert_path", ""))).expanduser()
        key = Path(str(data.get("client_key_path", ""))).expanduser()
        ready = cert.is_file() and key.is_file()
        last_error = _optional(getattr(self.client, "cloud_last_error", None))
        connected = bool(ready and not last_error)
        return CloudState(
            status="connected" if connected else "error" if last_error else "not_ready",
            connected=connected,
            authenticated=connected,
            endpoint="https://www.myhomeweb.com",
            last_request=_iso(getattr(self.client, "cloud_last_request_at", None)),
            last_response=_iso(getattr(self.client, "cloud_last_response_at", None)),
            last_error=last_error,
            certificate_ready=ready,
        )

    def sip(self) -> SipState:
        data = self._entry.data
        port = data.get("port")
        try:
            parsed_port = int(port) if port is not None else None
        except (TypeError, ValueError):
            parsed_port = None
        return SipState(
            registered=bool(getattr(self.client, "registered", False)),
            status=_optional(getattr(self.client, "last_status", None)),
            account=_optional(data.get("sip_account")),
            server=_optional(data.get("server")),
            port=parsed_port,
            transport="tls",
            dialog_state=str(getattr(self.client, "dialog_state", "idle") or "idle"),
            last_method=_optional(getattr(self.client, "last_sip_method", None)),
            last_call_id=_optional(getattr(self.client, "last_call_id", None)),
            last_error=_optional(getattr(self.client, "last_error", None)),
        )

    def dialog(self) -> DialogState:
        return DialogState(
            state=str(getattr(self.client, "dialog_state", "idle") or "idle"),
            call_state=_optional(getattr(self.client, "call_state", None)),
            caller=_optional(getattr(self.client, "last_caller", None)),
            caller_uri=_optional(getattr(self.client, "last_caller_uri", None)),
            caller_domain=_optional(getattr(self.client, "last_caller_domain", None)),
            caller_tag=_optional(getattr(self.client, "last_caller_tag", None)),
            last_method=_optional(getattr(self.client, "last_sip_method", None)),
            call_id=_optional(getattr(self.client, "last_call_id", None)),
            started_at=_iso(getattr(self.client, "call_started_at", None)),
            ended_at=_iso(getattr(self.client, "call_ended_at", None)),
        )

    def media(self) -> MediaState:
        session = _mapping(getattr(self.client, "last_completed_media_session", None))
        plan = _mapping(session.get("plan"))
        audio = _mapping(plan.get("audio"))
        video = _mapping(plan.get("video"))
        audio_ip, audio_port = _endpoint(audio)
        video_ip, video_port = _endpoint(video)
        suites = session.get("srtp_suites")
        suite = None
        if isinstance(suites, list) and suites:
            suite = str(suites[0])
        suite = (
            suite
            or _optional(plan.get("srtp_suite"))
            or _optional(getattr(self.client, "selected_srtp_suite", None))
        )
        history = getattr(self.client, "media_session_history", None)
        retained = len(history) if isinstance(history, list) else 0
        state = str(getattr(self.client, "media_runtime_state", "idle") or "idle")
        return MediaState(
            state=state,
            ready=state in {"prepared", "active", "closed"} or bool(session),
            audio_codec=_codec(audio)
            or _optional(getattr(self.client, "selected_audio_codec", None)),
            video_codec=_codec(video)
            or _optional(getattr(self.client, "selected_video_codec", None)),
            remote_audio_ip=audio_ip,
            remote_audio_port=audio_port,
            remote_video_ip=video_ip,
            remote_video_port=video_port,
            srtp_suite=suite,
            duration_seconds=_float_or_none(
                session.get("duration_seconds") or getattr(self.client, "last_call_duration", None)
            ),
            close_reason=_optional(session.get("closed_reason")),
            started_at=_iso(session.get("started_at")),
            closed_at=_iso(session.get("closed_at")),
            retained_sessions=retained,
        )

    def diagnostics(self) -> DiagnosticsState:
        sip = self.sip()
        media = self.media()
        issues: list[str] = []
        score = 100
        if not sip.registered:
            score -= 50
            issues.append("sip_not_registered")
        if sip.last_error:
            score -= 25
            issues.append("last_error_present")
        if media.state == "failed":
            score -= 25
            issues.append("media_failed")
        score = max(0, score)
        status = "healthy" if score >= 90 else "degraded" if score >= 60 else "unhealthy"
        return DiagnosticsState(
            status=status,
            score=score,
            issues=tuple(issues),
            sip_registered=sip.registered,
            dialog_state=sip.dialog_state,
            media_state=media.state,
            last_error=sip.last_error,
        )

    def devices(self) -> dict[str, Any]:
        """Return all logical runtime states keyed by device kind."""
        snapshot = self.snapshot()
        return {
            "gateway": snapshot.gateway,
            "cloud": snapshot.cloud,
            "sip": snapshot.sip,
            "dialog": snapshot.dialog,
            "media": snapshot.media,
            "diagnostics": snapshot.diagnostics,
        }

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(
            gateway=self.gateway(),
            cloud=self.cloud(),
            sip=self.sip(),
            dialog=self.dialog(),
            media=self.media(),
            diagnostics=self.diagnostics(),
        )


def _optional(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
