"""Minimal SIP-over-TLS client for BTDoor Security+."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import secrets
import ssl
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict, cast

from .const import CALL_TIMEOUT_SECONDS, DEFAULT_EXPIRES, DEFAULT_OPEN_COMMAND, USER_AGENT
from .media import (
    MediaPreparation,
    SrtpCryptoOffer,
    build_sdp_diff,
    media_snapshot,
    parse_crypto_attribute,
    prepare_media_offer,
)
from .sip_identity import parse_sip_identity

_LOGGER = logging.getLogger(__name__)


class BticinoSipError(Exception):
    """Base BTicino SIP error."""


class BticinoSipAuthenticationError(BticinoSipError):
    """SIP authentication failed."""


class BticinoSipConnectionError(BticinoSipError):
    """SIP connection failed."""


class BticinoSipNotFoundError(BticinoSipError):
    """The C300X target was temporarily not found by Flexisip."""


@dataclass(slots=True)
class SipResult:
    """Result of a SIP operation."""

    status: str
    code: int


@dataclass(slots=True)
class SdpMediaDescription:
    """Parsed SDP media section."""

    media: str
    port: int
    protocol: str
    payload_types: tuple[int, ...]
    connection_address: str | None
    direction: str
    codecs: tuple[str, ...]
    fmtp: dict[int, str]
    crypto: tuple[SrtpCryptoOffer, ...]
    rtcp_feedback: dict[int, tuple[str, ...]]


@dataclass(slots=True)
class SdpDescription:
    """Parsed SDP session description."""

    session_name: str | None
    connection_address: str | None
    direction: str
    media: tuple[SdpMediaDescription, ...]


@dataclass(slots=True)
class SipSession:
    """Registered SIP session."""

    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    identity_uri: str
    contact_uri: str
    proxy_uri: str
    username: str


class _StoredSipState(TypedDict, total=False):
    """Existing export-state schema; runtime restoration guards remain in place."""

    last_status: str | None
    last_caller: str | None
    last_caller_raw: str | None
    last_caller_uri: str | None
    last_caller_domain: str | None
    last_caller_tag: str | None
    last_caller_display_name: str | None
    last_call_id: str | None
    last_message: str | None
    call_state: str
    call_started_at: str | None
    call_ended_at: str | None
    last_call_duration: float | None
    call_count: int
    missed_call_count: int
    message_count: int
    last_message_at: str | None
    last_event_type: str | None
    last_event_data: dict[str, object]
    last_event_at: str | None
    reconnect_count: int
    last_error: str | None
    last_command_duration: float | None
    last_command_at: str | None
    dialog_state: str
    last_sip_method: str | None
    last_sdp_offer: str | None
    last_sdp_summary: str | None
    sdp_session_address: str | None
    sdp_audio_address: str | None
    sdp_audio_port: int | None
    sdp_audio_direction: str | None
    sdp_audio_codecs: list[str]
    sdp_audio_protocol: str | None
    sdp_audio_payload_types: list[int]
    sdp_audio_fmtp: dict[int, str]
    sdp_video_address: str | None
    sdp_video_port: int | None
    sdp_video_direction: str | None
    sdp_video_codecs: list[str]
    sdp_video_protocol: str | None
    sdp_video_payload_types: list[int]
    sdp_video_fmtp: dict[int, str]
    last_dialog_headers: dict[str, object]
    sip_timeline: list[dict[str, object]]
    runtime_session_id: str
    runtime_session_started_at: str
    last_info_body: str | None
    last_notify_event: str | None
    last_refer_to: str | None
    media_preparation: dict[str, object] | None
    last_media_preparation: dict[str, object] | None
    media_runtime_state: str
    media_runtime_call_id: str | None
    media_runtime_started_at: str | None
    media_runtime_prepared_at: str | None
    media_runtime_closed_at: str | None
    last_media_remote_sdp: str | None
    last_media_local_sdp: str | None
    last_media_sdp_diff: str | None
    media_trace_counter: int
    media_trace_id: str | None
    media_trace_state: str
    media_trace_error: str | None
    media_trace: list[dict[str, object]]
    media_session_history: list[dict[str, object]]
    last_completed_media_session: dict[str, object] | None
    sip_dispatcher_trace: list[dict[str, object]]
    sip_packet_count: int
    invite_received_count: int
    invite_dispatched_count: int
    invite_with_sdp_count: int
    invite_media_runtime_count: int


class _SdpSection(TypedDict):
    """Typed working buffer for one existing SDP media section."""

    media: str
    port: int
    protocol: str
    payloads: list[int]
    address: str | None
    direction: str
    rtpmap: dict[int, str]
    fmtp: dict[int, str]
    crypto: list[SrtpCryptoOffer]
    rtcp_fb: dict[int, list[str]]


class BticinoSipClient:
    """BTicino SIP client implementing the validated register/open flow."""

    def __init__(
        self,
        *,
        sip_account: str,
        sip_password: str,
        gateway_id: str,
        client_cert_path: str,
        client_key_path: str,
        server: str,
        port: int,
        verify_server: bool,
        debug_recorder=None,
    ) -> None:
        self.sip_account = sip_account.removeprefix("sip:").strip()
        self.sip_password = sip_password
        self.gateway_id = str(gateway_id).strip()
        self.client_cert_path = str(Path(client_cert_path).expanduser())
        self.client_key_path = str(Path(client_key_path).expanduser())
        self.server = server.strip()
        self.port = int(port)
        self.verify_server = verify_server
        self._debug = debug_recorder
        self.last_status: str | None = None
        self.registered = False
        self._session: SipSession | None = None
        self._lock = asyncio.Lock()
        self._keepalive_task: asyncio.Task[None] | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._pending: dict[
            tuple[str, str], asyncio.Future[tuple[bytes, str, dict[str, list[str]]]]
        ] = {}
        self._write_lock = asyncio.Lock()
        self.ringing = False
        self.last_caller: str | None = None
        self.last_caller_raw: str | None = None
        self.last_caller_uri: str | None = None
        self.last_caller_domain: str | None = None
        self.last_caller_tag: str | None = None
        self.last_caller_display_name: str | None = None
        self.last_call_id: str | None = None
        self.last_message: str | None = None
        self.call_state = "idle"
        self.call_started_at: datetime | None = None
        self.call_ended_at: datetime | None = None
        self.last_call_duration: float | None = None
        self.call_count = 0
        self.missed_call_count = 0
        self.message_count = 0
        self.last_message_at: datetime | None = None
        self._message_challenge: str | None = None
        self._message_auth_name = "Proxy-Authorization"
        self._message_nc = 0
        self._listeners: set[Callable[[str, dict[str, object]], None]] = set()
        self.last_event_type: str | None = None
        self.last_event_data: dict[str, object] = {}
        self.last_event_at: datetime | None = None
        self.connected_at: datetime | None = None
        self.last_keepalive_at: datetime | None = None
        self.last_error: str | None = None
        self.reconnect_count = 0
        self.last_command_duration: float | None = None
        self.last_command_at: datetime | None = None
        self._ever_registered = False
        self._call_timeout_task: asyncio.Task[None] | None = None
        self._active_call_id: str | None = None
        self._recent_messages: deque[tuple[str, str]] = deque(maxlen=50)
        # Milestone 4.1: SIP dialog/transaction foundation.
        self.dialog_state = "idle"
        self.last_sip_method: str | None = None
        self.last_sdp_offer: str | None = None
        self.last_sdp_summary: str | None = None
        self.sdp_session_address: str | None = None
        self.sdp_audio_address: str | None = None
        self.sdp_audio_port: int | None = None
        self.sdp_audio_direction: str | None = None
        self.sdp_audio_codecs: tuple[str, ...] = ()
        self.sdp_audio_protocol: str | None = None
        self.sdp_audio_payload_types: tuple[int, ...] = ()
        self.sdp_audio_fmtp: dict[int, str] = {}
        self.sdp_video_address: str | None = None
        self.sdp_video_port: int | None = None
        self.sdp_video_direction: str | None = None
        self.sdp_video_codecs: tuple[str, ...] = ()
        self.sdp_video_protocol: str | None = None
        self.sdp_video_payload_types: tuple[int, ...] = ()
        self.sdp_video_fmtp: dict[int, str] = {}
        self.last_dialog_headers: dict[str, object] = {}
        self.sip_timeline: deque[dict[str, object]] = deque(maxlen=100)
        self.runtime_session_id = uuid.uuid4().hex[:12]
        self.runtime_session_started_at = datetime.now(UTC)
        self.last_info_body: str | None = None
        self.last_notify_event: str | None = None
        self.last_refer_to: str | None = None
        self._invite_headers: dict[str, list[str]] | None = None
        self._invite_request_uri: str | None = None
        self._invite_local_tag: str | None = None
        self.media_preparation: MediaPreparation | None = None
        self.last_media_preparation: dict[str, object] | None = None
        self.media_runtime_state = "idle"
        self.media_runtime_call_id: str | None = None
        self.media_runtime_started_at: datetime | None = None
        self.media_runtime_prepared_at: datetime | None = None
        self.media_runtime_closed_at: datetime | None = None
        self.last_media_remote_sdp: str | None = None
        self.last_media_local_sdp: str | None = None
        self.last_media_sdp_diff: str | None = None
        self.media_trace_counter = 0
        self.media_trace_id: str | None = None
        self.media_trace_state = "idle"
        self.media_trace_error: str | None = None
        self.media_trace: deque[dict[str, object]] = deque(maxlen=100)
        self.media_session_history: deque[dict[str, object]] = deque(maxlen=10)
        self.last_completed_media_session: dict[str, object] | None = None
        self.sip_dispatcher_trace: deque[dict[str, object]] = deque(maxlen=250)
        self.sip_packet_count = 0
        self.invite_received_count = 0
        self.invite_dispatched_count = 0
        self.invite_with_sdp_count = 0
        self.invite_media_runtime_count = 0

    @property
    def sip_dispatcher_diagnostics(self) -> dict[str, object]:
        """Return bounded SIP dispatcher instrumentation and counters."""
        return {
            "packet_count": self.sip_packet_count,
            "invite_received_count": self.invite_received_count,
            "invite_dispatched_count": self.invite_dispatched_count,
            "invite_with_sdp_count": self.invite_with_sdp_count,
            "invite_media_runtime_count": self.invite_media_runtime_count,
            "last_method": self.last_sip_method,
            "trace_count": len(self.sip_dispatcher_trace),
            "trace": list(self.sip_dispatcher_trace),
        }

    def _trace_dispatcher(
        self,
        stage: str,
        *,
        method: str | None = None,
        status: str = "ok",
        packet_id: int | None = None,
        **details: object,
    ) -> None:
        """Record one non-sensitive SIP dispatcher step."""
        record: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "runtime_session_id": self.runtime_session_id,
            "packet_id": packet_id,
            "stage": stage,
            "method": method,
            "status": status,
            "details": details,
        }
        self.sip_dispatcher_trace.append(record)
        if self._debug is not None:
            self._debug.record("sip", "dispatcher_trace", **record)

    @property
    def media_plan(self) -> dict[str, object] | None:
        """Return current media preparation or the last detached snapshot."""
        if self.media_preparation is not None:
            return self.media_preparation.public_dict()
        return self.last_media_preparation

    @property
    def media_runtime(self) -> dict[str, object]:
        """Return observable non-sensitive media runtime state."""
        plan = self.media_plan
        return {
            "state": self.media_runtime_state,
            "call_id": self.media_runtime_call_id,
            "started_at": self.media_runtime_started_at.isoformat()
            if self.media_runtime_started_at
            else None,
            "prepared_at": self.media_runtime_prepared_at.isoformat()
            if self.media_runtime_prepared_at
            else None,
            "closed_at": self.media_runtime_closed_at.isoformat()
            if self.media_runtime_closed_at
            else None,
            "ready_for_answer": bool(
                plan and plan.get("state") in {"prepared", "released"} and not plan.get("issues")
            ),
            "plan": plan,
            "remote_sdp_available": bool(self.last_media_remote_sdp),
            "local_sdp_available": bool(self.last_media_local_sdp),
            "sdp_diff_available": bool(self.last_media_sdp_diff),
            "trace_id": self.media_trace_id,
            "trace_state": self.media_trace_state,
            "trace_error": self.media_trace_error,
            "trace_step_count": len(self.media_trace),
        }

    @property
    def media_session_metrics(self) -> dict[str, object]:
        """Return aggregate metrics for the bounded completed-session history."""
        sessions = list(self.media_session_history)
        durations = [
            float(cast(int | float, item["duration_seconds"]))
            for item in sessions
            if isinstance(item.get("duration_seconds"), (int, float))
        ]
        codecs: dict[str, int] = {}
        close_reasons: dict[str, int] = {}
        for item in sessions:
            reason = str(item.get("closed_reason") or "unknown")
            close_reasons[reason] = close_reasons.get(reason, 0) + 1
            plan = item.get("plan")
            if isinstance(plan, dict):
                for section in ("audio", "video"):
                    media = plan.get(section)
                    codec = media.get("codec") if isinstance(media, dict) else None
                    if codec:
                        key = str(codec)
                        codecs[key] = codecs.get(key, 0) + 1
        return {
            "retained_sessions": len(sessions),
            "history_limit": self.media_session_history.maxlen,
            "average_duration_seconds": (
                round(sum(durations) / len(durations), 3) if durations else None
            ),
            "codec_usage": codecs,
            "close_reasons": close_reasons,
            "last_closed_at": sessions[-1].get("closed_at") if sessions else None,
        }

    @property
    def media_diagnostics(self) -> dict[str, object]:
        """Return current state plus persistent completed-session diagnostics."""
        return {
            "current": self.media_runtime,
            "last_completed": self.last_completed_media_session,
            "history": list(self.media_session_history),
            "metrics": self.media_session_metrics,
        }

    @property
    def media_instrumentation(self) -> dict[str, object]:
        """Return the current Media Runtime instrumentation state."""
        return {
            "trace_id": self.media_trace_id,
            "state": self.media_trace_state,
            "error": self.media_trace_error,
            "steps": list(self.media_trace),
            "step_count": len(self.media_trace),
            "media_plan_available": self.media_plan is not None,
            "remote_sdp_available": bool(self.last_media_remote_sdp),
            "local_sdp_available": bool(self.last_media_local_sdp),
            "runtime": self.media_runtime,
            "last_completed": self.last_completed_media_session,
            "metrics": self.media_session_metrics,
        }

    def _start_media_trace(self, call_id: str | None) -> str:
        """Start a new trace for one incoming INVITE."""
        self.media_trace_counter += 1
        self.media_trace_id = f"MT-{self.media_trace_counter:06d}"
        self.media_trace_state = "started"
        self.media_trace_error = None
        self.media_trace.clear()
        self._trace_media("invite_received", status="ok", call_id=call_id)
        return self.media_trace_id

    def _trace_media(
        self,
        stage: str,
        *,
        status: str,
        **details: object,
    ) -> None:
        """Record one observable step in the Media Runtime pipeline."""
        record: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "runtime_session_id": self.runtime_session_id,
            "trace_id": self.media_trace_id,
            "stage": stage,
            "status": status,
            "call_id": self.media_runtime_call_id or self._active_call_id or self.last_call_id,
            "details": details,
        }
        self.media_trace.append(record)
        self.media_trace_state = stage if status == "ok" else "failed"
        if status != "ok":
            self.media_trace_error = str(details.get("error") or stage)
        if self._debug is not None:
            self._debug.record("media", "media_trace", **record)

    def add_listener(
        self, listener: Callable[[str, dict[str, object]], None]
    ) -> Callable[[], None]:
        """Subscribe to integration events."""
        self._listeners.add(listener)

        def _remove() -> None:
            self._listeners.discard(listener)

        return _remove

    def _notify(self, event_type: str, **data: object) -> None:
        if self._debug is not None:
            self._debug.record("sip", event_type, **data)
        self.last_event_type = event_type
        self.last_event_data = data
        self.last_event_at = datetime.now(UTC)
        for listener in tuple(self._listeners):
            listener(event_type, data)

    def export_state(self) -> dict[str, object]:
        """Return persistent event/statistics state."""

        def iso(value: datetime | None) -> str | None:
            return value.isoformat() if value else None

        return {
            "last_status": self.last_status,
            "last_caller": self.last_caller,
            "last_caller_raw": self.last_caller_raw,
            "last_caller_uri": self.last_caller_uri,
            "last_caller_domain": self.last_caller_domain,
            "last_caller_tag": self.last_caller_tag,
            "last_caller_display_name": self.last_caller_display_name,
            "last_call_id": self.last_call_id,
            "last_message": self.last_message,
            "call_state": self.call_state,
            "call_started_at": iso(self.call_started_at),
            "call_ended_at": iso(self.call_ended_at),
            "last_call_duration": self.last_call_duration,
            "call_count": self.call_count,
            "missed_call_count": self.missed_call_count,
            "message_count": self.message_count,
            "last_message_at": iso(self.last_message_at),
            "last_event_type": self.last_event_type,
            "last_event_data": self.last_event_data,
            "last_event_at": iso(self.last_event_at),
            "reconnect_count": self.reconnect_count,
            "last_error": self.last_error,
            "last_command_duration": self.last_command_duration,
            "last_command_at": iso(self.last_command_at),
            "dialog_state": self.dialog_state,
            "last_sip_method": self.last_sip_method,
            "last_sdp_offer": self.last_sdp_offer,
            "last_sdp_summary": self.last_sdp_summary,
            "sdp_session_address": self.sdp_session_address,
            "sdp_audio_address": self.sdp_audio_address,
            "sdp_audio_port": self.sdp_audio_port,
            "sdp_audio_direction": self.sdp_audio_direction,
            "sdp_audio_codecs": list(self.sdp_audio_codecs),
            "sdp_audio_protocol": self.sdp_audio_protocol,
            "sdp_audio_payload_types": list(self.sdp_audio_payload_types),
            "sdp_audio_fmtp": dict(self.sdp_audio_fmtp),
            "sdp_video_address": self.sdp_video_address,
            "sdp_video_port": self.sdp_video_port,
            "sdp_video_direction": self.sdp_video_direction,
            "sdp_video_codecs": list(self.sdp_video_codecs),
            "sdp_video_protocol": self.sdp_video_protocol,
            "sdp_video_payload_types": list(self.sdp_video_payload_types),
            "sdp_video_fmtp": dict(self.sdp_video_fmtp),
            "last_dialog_headers": dict(self.last_dialog_headers),
            "sip_timeline": list(self.sip_timeline),
            "runtime_session_id": self.runtime_session_id,
            "runtime_session_started_at": self.runtime_session_started_at.isoformat(),
            "last_info_body": self.last_info_body,
            "last_notify_event": self.last_notify_event,
            "last_refer_to": self.last_refer_to,
            "media_preparation": self.media_preparation.public_dict()
            if self.media_preparation
            else None,
            "last_media_preparation": self.last_media_preparation,
            "media_runtime_state": self.media_runtime_state,
            "media_runtime_call_id": self.media_runtime_call_id,
            "media_runtime_started_at": iso(self.media_runtime_started_at),
            "media_runtime_prepared_at": iso(self.media_runtime_prepared_at),
            "media_runtime_closed_at": iso(self.media_runtime_closed_at),
            "last_media_remote_sdp": self.last_media_remote_sdp,
            "last_media_local_sdp": self.last_media_local_sdp,
            "last_media_sdp_diff": self.last_media_sdp_diff,
            "media_trace_counter": self.media_trace_counter,
            "media_trace_id": self.media_trace_id,
            "media_trace_state": self.media_trace_state,
            "media_trace_error": self.media_trace_error,
            "media_trace": list(self.media_trace),
            "media_session_history": list(self.media_session_history),
            "last_completed_media_session": self.last_completed_media_session,
            "sip_dispatcher_trace": list(self.sip_dispatcher_trace),
            "sip_packet_count": self.sip_packet_count,
            "invite_received_count": self.invite_received_count,
            "invite_dispatched_count": self.invite_dispatched_count,
            "invite_with_sdp_count": self.invite_with_sdp_count,
            "invite_media_runtime_count": self.invite_media_runtime_count,
        }

    def restore_state(self, state: dict[str, object] | None) -> None:
        """Restore persistent event/statistics state."""
        if not state:
            return

        stored = cast(_StoredSipState, state)

        def dt(name: str) -> datetime | None:
            value = stored.get(name)
            if not isinstance(value, str) or not value:
                return None
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None

        self.last_status = (
            stored.get("last_status") if isinstance(stored.get("last_status"), str) else None
        )
        stored_caller = (
            stored.get("last_caller") if isinstance(stored.get("last_caller"), str) else None
        )
        stored_raw = (
            stored.get("last_caller_raw")
            if isinstance(stored.get("last_caller_raw"), str)
            else stored_caller
        )
        restored_identity = parse_sip_identity(stored_raw)
        self.last_caller = restored_identity.label if restored_identity else stored_caller
        self.last_caller_raw = restored_identity.raw if restored_identity else stored_raw
        self.last_caller_uri = (
            stored.get("last_caller_uri")
            if isinstance(stored.get("last_caller_uri"), str)
            else restored_identity.uri
            if restored_identity
            else None
        )
        self.last_caller_domain = (
            stored.get("last_caller_domain")
            if isinstance(stored.get("last_caller_domain"), str)
            else restored_identity.domain
            if restored_identity
            else None
        )
        self.last_caller_tag = (
            stored.get("last_caller_tag")
            if isinstance(stored.get("last_caller_tag"), str)
            else restored_identity.tag
            if restored_identity
            else None
        )
        self.last_caller_display_name = (
            stored.get("last_caller_display_name")
            if isinstance(stored.get("last_caller_display_name"), str)
            else restored_identity.display_name
            if restored_identity
            else None
        )
        self.last_call_id = (
            stored.get("last_call_id") if isinstance(stored.get("last_call_id"), str) else None
        )
        self.last_message = (
            stored.get("last_message") if isinstance(stored.get("last_message"), str) else None
        )
        self.call_state = str(stored.get("call_state", "idle"))
        self.call_started_at = dt("call_started_at")
        self.call_ended_at = dt("call_ended_at")
        self.last_call_duration = (
            stored.get("last_call_duration")
            if isinstance(stored.get("last_call_duration"), (int, float))
            else None
        )
        self.call_count = int(stored.get("call_count", 0) or 0)
        self.missed_call_count = int(stored.get("missed_call_count", 0) or 0)
        self.message_count = int(stored.get("message_count", 0) or 0)
        self.last_message_at = dt("last_message_at")
        self.last_event_type = (
            stored.get("last_event_type")
            if isinstance(stored.get("last_event_type"), str)
            else None
        )
        self.last_event_data = (
            cast(dict[str, object], stored.get("last_event_data"))
            if isinstance(stored.get("last_event_data"), dict)
            else {}
        )
        self.last_event_at = dt("last_event_at")
        self.reconnect_count = int(stored.get("reconnect_count", 0) or 0)
        self.last_error = (
            stored.get("last_error") if isinstance(stored.get("last_error"), str) else None
        )
        self.last_command_duration = (
            stored.get("last_command_duration")
            if isinstance(stored.get("last_command_duration"), (int, float))
            else None
        )
        self.last_command_at = dt("last_command_at")
        self.dialog_state = str(stored.get("dialog_state", "idle"))
        self.last_sip_method = (
            stored.get("last_sip_method")
            if isinstance(stored.get("last_sip_method"), str)
            else None
        )
        self.last_sdp_offer = (
            stored.get("last_sdp_offer") if isinstance(stored.get("last_sdp_offer"), str) else None
        )
        self.last_sdp_summary = (
            stored.get("last_sdp_summary")
            if isinstance(stored.get("last_sdp_summary"), str)
            else None
        )
        self.sdp_session_address = (
            stored.get("sdp_session_address")
            if isinstance(stored.get("sdp_session_address"), str)
            else None
        )
        self.sdp_audio_address = (
            stored.get("sdp_audio_address")
            if isinstance(stored.get("sdp_audio_address"), str)
            else None
        )
        self.sdp_audio_port = (
            stored.get("sdp_audio_port") if isinstance(stored.get("sdp_audio_port"), int) else None
        )
        self.sdp_audio_direction = (
            stored.get("sdp_audio_direction")
            if isinstance(stored.get("sdp_audio_direction"), str)
            else None
        )
        self.sdp_audio_codecs = tuple(str(x) for x in stored.get("sdp_audio_codecs", []) or [])
        self.sdp_audio_protocol = stored.get("sdp_audio_protocol") or None
        self.sdp_audio_payload_types = tuple(
            int(x) for x in stored.get("sdp_audio_payload_types", []) or []
        )
        self.sdp_audio_fmtp = {
            int(k): str(v) for k, v in dict(stored.get("sdp_audio_fmtp", {}) or {}).items()
        }
        self.sdp_video_address = stored.get("sdp_video_address") or None
        self.sdp_video_port = (
            stored.get("sdp_video_port") if isinstance(stored.get("sdp_video_port"), int) else None
        )
        self.sdp_video_direction = (
            stored.get("sdp_video_direction")
            if isinstance(stored.get("sdp_video_direction"), str)
            else None
        )
        self.sdp_video_codecs = tuple(str(x) for x in stored.get("sdp_video_codecs", []) or [])
        self.sdp_video_protocol = stored.get("sdp_video_protocol") or None
        self.sdp_video_payload_types = tuple(
            int(x) for x in stored.get("sdp_video_payload_types", []) or []
        )
        self.sdp_video_fmtp = {
            int(k): str(v) for k, v in dict(stored.get("sdp_video_fmtp", {}) or {}).items()
        }
        self.last_dialog_headers = dict(stored.get("last_dialog_headers", {}) or {})
        self.sip_timeline = deque(
            (dict(x) for x in stored.get("sip_timeline", []) or []), maxlen=100
        )
        self.last_info_body = stored.get("last_info_body") or None
        self.last_notify_event = (
            stored.get("last_notify_event")
            if isinstance(stored.get("last_notify_event"), str)
            else None
        )
        self.last_refer_to = (
            stored.get("last_refer_to") if isinstance(stored.get("last_refer_to"), str) else None
        )
        self.last_media_preparation = (
            stored.get("last_media_preparation")
            if isinstance(stored.get("last_media_preparation"), dict)
            else None
        )
        self.media_runtime_state = str(stored.get("media_runtime_state", "idle") or "idle")
        self.media_runtime_call_id = (
            stored.get("media_runtime_call_id")
            if isinstance(stored.get("media_runtime_call_id"), str)
            else None
        )
        self.media_runtime_started_at = dt("media_runtime_started_at")
        self.media_runtime_prepared_at = dt("media_runtime_prepared_at")
        self.media_runtime_closed_at = dt("media_runtime_closed_at")
        self.last_media_remote_sdp = (
            stored.get("last_media_remote_sdp")
            if isinstance(stored.get("last_media_remote_sdp"), str)
            else None
        )
        self.last_media_local_sdp = (
            stored.get("last_media_local_sdp")
            if isinstance(stored.get("last_media_local_sdp"), str)
            else None
        )
        self.last_media_sdp_diff = (
            stored.get("last_media_sdp_diff")
            if isinstance(stored.get("last_media_sdp_diff"), str)
            else None
        )
        self.media_trace_counter = int(stored.get("media_trace_counter", 0) or 0)
        self.media_trace_id = (
            stored.get("media_trace_id") if isinstance(stored.get("media_trace_id"), str) else None
        )
        self.media_trace_state = str(stored.get("media_trace_state", "idle") or "idle")
        self.media_trace_error = (
            stored.get("media_trace_error")
            if isinstance(stored.get("media_trace_error"), str)
            else None
        )
        self.media_trace = deque(
            (dict(x) for x in stored.get("media_trace", []) or [] if isinstance(x, dict)),
            maxlen=100,
        )
        self.media_session_history = deque(
            (dict(x) for x in stored.get("media_session_history", []) or [] if isinstance(x, dict)),
            maxlen=10,
        )
        stored_completed = stored.get("last_completed_media_session")
        self.last_completed_media_session = (
            dict(stored_completed)
            if isinstance(stored_completed, dict)
            else (dict(self.media_session_history[-1]) if self.media_session_history else None)
        )
        self.sip_dispatcher_trace = deque(
            (dict(x) for x in stored.get("sip_dispatcher_trace", []) or [] if isinstance(x, dict)),
            maxlen=250,
        )
        self.sip_packet_count = int(stored.get("sip_packet_count", 0) or 0)
        self.invite_received_count = int(stored.get("invite_received_count", 0) or 0)
        self.invite_dispatched_count = int(stored.get("invite_dispatched_count", 0) or 0)
        self.invite_with_sdp_count = int(stored.get("invite_with_sdp_count", 0) or 0)
        self.invite_media_runtime_count = int(stored.get("invite_media_runtime_count", 0) or 0)

    @property
    def current_session_timeline(self) -> list[dict[str, object]]:
        """Return SIP timeline records generated by the current runtime session."""
        return [
            dict(item)
            for item in self.sip_timeline
            if item.get("session_id") == self.runtime_session_id
        ]

    def reset_statistics(self) -> None:
        """Reset persistent counters and historical diagnostics."""
        self.call_count = 0
        self.missed_call_count = 0
        self.message_count = 0
        self.reconnect_count = 0
        self.last_call_duration = None
        self.last_message = None
        self.last_message_at = None
        self.last_error = None
        self.last_command_duration = None
        self.last_command_at = None
        self.sip_timeline.clear()
        self._notify("statistics_reset", session_id=self.runtime_session_id)

    @property
    def digest_username(self) -> str:
        """Return the Digest username validated against Flexisip."""
        return self.sip_account.split("@", 1)[0]

    @property
    def target_uri(self) -> str:
        """Return the official C300X target URI."""
        return f"sip:c300x@{self.gateway_id}.bs.iotleg.com"

    async def async_start(self) -> None:
        """Establish and keep a registered SIP connection ready.

        Digest prefetch is an optional optimization. Some Flexisip nodes do
        not answer OPTIONS requests, so failure or timeout must never prevent
        the config entry from loading.
        """
        async with self._lock:
            # Keep the registered TLS session ready. Do not send an OPTIONS
            # priming request on this persistent stream: some Flexisip nodes
            # answer after our timeout, leaving a stale response that can be
            # mistaken for the next MESSAGE response. The first MESSAGE performs
            # the normal 407 negotiation and the challenge is cached afterwards.
            await self._async_ensure_session()
        if self._keepalive_task is None or self._keepalive_task.done():
            self._keepalive_task = asyncio.create_task(self._async_keepalive_loop())

    async def async_stop(self) -> None:
        """Stop keepalive and close the persistent session."""
        if self._keepalive_task is not None:
            self._keepalive_task.cancel()
            try:
                await self._keepalive_task
            except asyncio.CancelledError:
                pass
            self._keepalive_task = None
        if self._call_timeout_task is not None:
            self._call_timeout_task.cancel()
            try:
                await self._call_timeout_task
            except asyncio.CancelledError:
                pass
            self._call_timeout_task = None
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None
        async with self._lock:
            await self._async_drop_session()
        self._release_media_preparation()

    async def async_test_connection(self) -> SipResult:
        """Validate SIP without disrupting the persistent registered session."""
        session = self._session
        if (
            self.registered
            and session is not None
            and not session.writer.is_closing()
            and not session.reader.at_eof()
        ):
            return SipResult(
                status=self.last_status or "SIP/2.0 200 Registration successful",
                code=200,
            )

        # No live production session exists. Perform a temporary REGISTER while
        # preserving counters and public runtime state used by Home Assistant.
        previous_registered = self.registered
        previous_connected_at = self.connected_at
        previous_ever_registered = self._ever_registered
        previous_reconnect_count = self.reconnect_count
        try:
            probe_session, result = await self._async_register()
            await self._async_close_raw(probe_session.writer)
            return result
        finally:
            self.registered = previous_registered
            self.connected_at = previous_connected_at
            self._ever_registered = previous_ever_registered
            self.reconnect_count = previous_reconnect_count

    async def async_open_gate(self) -> SipResult:
        """Send the command over the persistent registered connection.

        Some Flexisip nodes return a transient 404 for the first MESSAGE after
        a fresh registration. Retrying the same authenticated command after a
        short delay is safe because a 404 means the command was not delivered.
        """
        started = asyncio.get_running_loop().time()
        self.last_command_at = datetime.now(UTC)
        async with self._lock:
            for connection_attempt in range(2):
                try:
                    session = await self._async_ensure_session()
                    for target_attempt in range(2):
                        try:
                            result = await self._async_send_message(
                                session, self.target_uri, DEFAULT_OPEN_COMMAND
                            )
                            self.last_status = result.status
                            self.last_error = None
                            self.last_command_duration = max(
                                0.0, asyncio.get_running_loop().time() - started
                            )
                            self._notify(
                                "gate_opened",
                                status=result.status,
                                code=result.code,
                                target=self.target_uri,
                                duration_seconds=self.last_command_duration,
                            )
                            return result
                        except BticinoSipNotFoundError:
                            if target_attempt:
                                raise
                            _LOGGER.debug("C300X target returned a transient 404; retrying once")
                            await asyncio.sleep(1.0)
                except BticinoSipAuthenticationError as err:
                    # Some Flexisip nodes reject the first authenticated MESSAGE
                    # after a fresh REGISTER with a transient 403. The command was
                    # not delivered, so it is safe to invalidate the cached Digest
                    # challenge, rebuild the registered TLS session, and retry once.
                    self.last_status = str(err)
                    self.last_error = str(err)
                    self._message_challenge = None
                    self._message_nc = 0
                    await self._async_drop_session()
                    if connection_attempt:
                        self._notify(
                            "gate_open_failed",
                            error=str(err),
                            target=self.target_uri,
                            duration_seconds=max(
                                0.0,
                                asyncio.get_running_loop().time() - started,
                            ),
                        )
                        raise
                    _LOGGER.debug(
                        "Flexisip returned a transient authentication error on the "
                        "first gate command; rebuilding the SIP session and retrying once: %s",
                        err,
                    )
                    await asyncio.sleep(1.0)
                except (BticinoSipConnectionError, OSError, ssl.SSLError):
                    await self._async_drop_session()
                    if connection_attempt:
                        raise
        raise BticinoSipConnectionError("Unable to establish SIP session")

    async def async_reject_call(self) -> SipResult:
        """Reject the currently ringing incoming call without starting media."""
        async with self._lock:
            if not self.ringing or self._invite_headers is None:
                raise BticinoSipError("No incoming call is currently ringing")
            session = await self._async_ensure_session()
            await self._async_send_response(
                session.writer,
                486,
                "Busy Here",
                self._invite_headers,
                add_to_tag=True,
                to_tag=self._invite_local_tag,
            )
            now = datetime.now(UTC)
            self.ringing = False
            self.call_state = "rejected"
            self.dialog_state = "terminated"
            self.call_ended_at = now
            if self.call_started_at is not None:
                self.last_call_duration = max(0.0, (now - self.call_started_at).total_seconds())
            self._notify(
                "call_rejected",
                caller=self.last_caller,
                call_id=self.last_call_id,
                ended_at=now.isoformat(),
                duration_seconds=self.last_call_duration,
            )
            self._clear_active_dialog("rejected")
            return SipResult(status="SIP/2.0 486 Busy Here", code=486)

    def _release_media_preparation(self, closed_reason: str | None = None) -> None:
        """Release media resources and persist an export-safe completed snapshot."""
        if self.media_preparation is not None:
            self.last_media_preparation = media_snapshot(self.media_preparation)
            self.media_preparation.close()
            released = media_snapshot(self.media_preparation)
            if released is not None:
                self.last_media_preparation = released
            self.media_preparation = None
        if self.media_runtime_state in {"preparing", "prepared", "failed"}:
            self.media_runtime_state = "closed"
            self.media_trace_state = "closed"
            self.media_runtime_closed_at = datetime.now(UTC)
            self._trace_media(
                "media_session_closed",
                status="ok",
                snapshot_available=self.last_media_preparation is not None,
            )
            completed = {
                **self.media_runtime,
                "closed_reason": closed_reason or self.call_state or "unknown",
                "duration_seconds": (
                    max(
                        0.0,
                        (
                            self.media_runtime_closed_at - self.media_runtime_started_at
                        ).total_seconds(),
                    )
                    if self.media_runtime_started_at
                    else None
                ),
                "trace": list(self.media_trace),
                "remote_sdp_available": bool(self.last_media_remote_sdp),
                "local_sdp_available": bool(self.last_media_local_sdp),
                "sdp_diff_available": bool(self.last_media_sdp_diff),
            }
            self.last_completed_media_session = completed
            self.media_session_history.append(completed)
            self._notify(
                "media_session_closed",
                call_id=self.media_runtime_call_id,
                closed_at=self.media_runtime_closed_at.isoformat(),
                closed_reason=completed["closed_reason"],
                media_runtime=self.media_runtime,
            )

    def _clear_active_dialog(self, closed_reason: str | None = None) -> None:
        """Clear ephemeral incoming-dialog state while retaining diagnostics."""
        self._release_media_preparation(closed_reason)
        self._active_call_id = None
        self._invite_headers = None
        self._invite_request_uri = None
        self._invite_local_tag = None

    async def _async_ensure_session(self) -> SipSession:
        session = self._session
        if (
            session is not None
            and not session.writer.is_closing()
            and not session.reader.at_eof()
            and self.registered
        ):
            return session
        await self._async_drop_session()
        session, _ = await self._async_register()
        self._session = session
        if self._reader_task is None or self._reader_task.done():
            self._reader_task = asyncio.create_task(self._async_reader_loop(session))
        return session

    async def _async_prime_proxy_auth(self) -> None:
        """Fetch a Digest nonce safely using OPTIONS."""
        if self._message_challenge is not None or self._session is None:
            return
        session = self._session
        request = self._build_request(
            method="OPTIONS",
            request_uri=self.target_uri,
            identity_uri=session.identity_uri,
            contact_uri=session.contact_uri,
            cseq=1,
            call_id=self._call_id(),
            from_tag=self._tag(),
            route=session.proxy_uri,
        )
        try:
            await self._async_write(session.writer, request)
            _, status, headers = await self._read_final_response(session.reader, timeout=10)
            if self._status_code(status) in (401, 407):
                self._message_challenge, self._message_auth_name = self._challenge(headers)
                self._message_nc = 0
        except (
            TimeoutError,
            asyncio.IncompleteReadError,
            ConnectionError,
            OSError,
            ssl.SSLError,
            BticinoSipError,
        ) as err:
            _LOGGER.debug(
                "Unable to prime proxy authentication; continuing without cached nonce: %s",
                err,
            )

    async def _async_keepalive_loop(self) -> None:
        """Keep the TLS connection alive through NAT and reconnect if needed."""
        try:
            while True:
                await asyncio.sleep(25)
                async with self._lock:
                    try:
                        session = await self._async_ensure_session()
                        await self._async_write(session.writer, b"\r\n")
                        self.last_keepalive_at = datetime.now(UTC)
                    except (BticinoSipError, OSError, ssl.SSLError) as err:
                        self.last_error = str(err)
                        await self._async_drop_session()
        except asyncio.CancelledError:
            raise

    def _build_ssl_context(self, cert: Path, key: Path) -> ssl.SSLContext:
        """Build the TLS context outside Home Assistant's event loop."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        context.check_hostname = self.verify_server
        context.verify_mode = ssl.CERT_REQUIRED if self.verify_server else ssl.CERT_NONE
        if self.verify_server:
            context.load_default_certs()
        context.load_cert_chain(certfile=str(cert), keyfile=str(key))
        return context

    async def _async_connect(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        cert = Path(self.client_cert_path)
        key = Path(self.client_key_path)
        cert_exists, key_exists = await asyncio.to_thread(lambda: (cert.is_file(), key.is_file()))
        if not cert_exists:
            raise BticinoSipConnectionError(f"Client certificate not found: {cert}")
        if not key_exists:
            raise BticinoSipConnectionError(f"Client key not found: {key}")

        context = await asyncio.to_thread(self._build_ssl_context, cert, key)

        try:
            return await asyncio.wait_for(
                asyncio.open_connection(
                    self.server,
                    self.port,
                    ssl=context,
                    server_hostname=self.server,
                ),
                timeout=20,
            )
        except (OSError, ssl.SSLError, TimeoutError) as err:
            raise BticinoSipConnectionError(str(err)) from err

    async def _async_register(self) -> tuple[SipSession, SipResult]:
        reader, writer = await self._async_connect()
        identity_uri = f"sip:{self.sip_account}"
        proxy_uri = f"sip:{self.server};transport=tls"
        contact_uri = f"sip:{self.sip_account};transport=tls"
        request_uri = f"sip:{self.server}"
        call_id = self._call_id()
        from_tag = self._tag()

        request = self._build_request(
            method="REGISTER",
            request_uri=request_uri,
            identity_uri=identity_uri,
            contact_uri=contact_uri,
            cseq=1,
            call_id=call_id,
            from_tag=from_tag,
            route=proxy_uri,
        )
        await self._async_write(writer, request)
        raw, status, headers = await self._read_final_response(reader)
        code = self._status_code(status)

        if code in (401, 407):
            challenge, auth_name = self._challenge(headers)
            auth = self._make_digest_auth(
                challenge,
                "REGISTER",
                request_uri,
                self.digest_username,
                self.sip_password,
            )
            request = self._build_request(
                method="REGISTER",
                request_uri=request_uri,
                identity_uri=identity_uri,
                contact_uri=contact_uri,
                cseq=2,
                call_id=call_id,
                from_tag=from_tag,
                route=proxy_uri,
                auth_header=auth,
                auth_name=auth_name,
            )
            await self._async_write(writer, request)
            raw, status, headers = await self._read_final_response(reader)
            code = self._status_code(status)

        if code != 200:
            await self._async_close_raw(writer)
            if code in (401, 403, 407):
                raise BticinoSipAuthenticationError(status)
            raise BticinoSipError(self._safe_preview(raw))

        reconnect = self._ever_registered
        self.registered = True
        self.connected_at = datetime.now(UTC)
        self.last_error = None
        self.last_status = status
        if reconnect:
            self.reconnect_count += 1
            self._notify(
                "connection_restored",
                status=status,
                server=self.server,
                port=self.port,
                reconnect_count=self.reconnect_count,
            )
        else:
            self._notify("registered", status=status, server=self.server, port=self.port)
        self._ever_registered = True
        return (
            SipSession(
                reader=reader,
                writer=writer,
                identity_uri=identity_uri,
                contact_uri=contact_uri,
                proxy_uri=proxy_uri,
                username=self.digest_username,
            ),
            SipResult(status=status, code=code),
        )

    async def _async_send_message(
        self, session: SipSession, target_uri: str, body: str
    ) -> SipResult:
        call_id = self._call_id()
        from_tag = self._tag()
        auth = None
        if self._message_challenge is not None:
            self._message_nc += 1
            auth = self._make_digest_auth(
                self._message_challenge,
                "MESSAGE",
                target_uri,
                session.username,
                self.sip_password,
                nc=self._message_nc,
            )
        request = self._build_request(
            method="MESSAGE",
            request_uri=target_uri,
            identity_uri=session.identity_uri,
            contact_uri=session.contact_uri,
            cseq=1,
            call_id=call_id,
            from_tag=from_tag,
            route=session.proxy_uri,
            auth_header=auth,
            auth_name=self._message_auth_name,
            body=body,
            content_type="text/plain;charset=UTF-8",
        )
        raw, status, headers = await self._async_exchange(
            session, request, call_id=call_id, cseq_method="MESSAGE", timeout=30
        )
        code = self._status_code(status)
        if code in (401, 407):
            self._message_challenge, self._message_auth_name = self._challenge(headers)
            self._message_nc = 1
            auth = self._make_digest_auth(
                self._message_challenge,
                "MESSAGE",
                target_uri,
                session.username,
                self.sip_password,
                nc=1,
            )
            request = self._build_request(
                method="MESSAGE",
                request_uri=target_uri,
                identity_uri=session.identity_uri,
                contact_uri=session.contact_uri,
                cseq=2,
                call_id=call_id,
                from_tag=from_tag,
                route=session.proxy_uri,
                auth_header=auth,
                auth_name=self._message_auth_name,
                body=body,
                content_type="text/plain;charset=UTF-8",
            )
            raw, status, _ = await self._async_exchange(
                session, request, call_id=call_id, cseq_method="MESSAGE", timeout=30
            )
            code = self._status_code(status)
        if code not in (200, 202):
            if code in (401, 403, 407):
                raise BticinoSipAuthenticationError(status)
            if code == 404:
                raise BticinoSipNotFoundError(self._safe_preview(raw))
            raise BticinoSipError(self._safe_preview(raw))
        return SipResult(status=status, code=code)

    async def _async_drop_session(self) -> None:
        session = self._session
        self._session = None
        current = asyncio.current_task()
        if self._reader_task is not None and self._reader_task is not current:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
        self._reader_task = None
        for future in self._pending.values():
            if not future.done():
                future.set_exception(BticinoSipConnectionError("SIP session closed"))
        self._pending.clear()
        was_registered = self.registered
        self.registered = False
        self.connected_at = None
        if was_registered:
            self._notify("disconnected", server=self.server, port=self.port)
        if session is not None:
            await self._async_close_raw(session.writer)

    async def _async_close(self, session: SipSession) -> None:
        await self._async_close_raw(session.writer)
        self.registered = False

    @staticmethod
    async def _async_close_raw(writer: asyncio.StreamWriter) -> None:
        writer.close()
        try:
            await writer.wait_closed()
        except (OSError, ssl.SSLError):
            pass

    async def _async_write(self, writer: asyncio.StreamWriter, data: bytes) -> None:
        if self._debug is not None:
            self._debug.protocol("out", data)
        async with self._write_lock:
            writer.write(data)
            await writer.drain()

    async def _async_exchange(
        self,
        session: SipSession,
        request: bytes,
        *,
        call_id: str,
        cseq_method: str,
        timeout: int,  # noqa: ASYNC109 - Preserve the SIP timeout contract (including test doubles).
    ) -> tuple[bytes, str, dict[str, list[str]]]:
        """Send a SIP request and wait for its final response."""
        key = (call_id, cseq_method.upper())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending[key] = future
        try:
            await self._async_write(session.writer, request)
            return await asyncio.wait_for(future, timeout)
        except TimeoutError as err:
            raise BticinoSipConnectionError(f"Timeout waiting for {cseq_method} response") from err
        finally:
            self._pending.pop(key, None)

    async def _async_reader_loop(self, session: SipSession) -> None:
        """Continuously receive SIP responses and unsolicited requests."""
        try:
            while not session.writer.is_closing():
                try:
                    raw = await self._read_sip_frame(session.reader, timeout=90)
                except TimeoutError:
                    # An idle SIP/TLS stream is normal. Keepalive traffic is
                    # outbound-only on some Flexisip nodes, so lack of inbound
                    # data must not be interpreted as a disconnect.
                    continue
                first_line, headers, body = self._parse_message(raw)
                self.sip_packet_count += 1
                packet_id = self.sip_packet_count
                self._trace_dispatcher(
                    "frame_parsed",
                    packet_id=packet_id,
                    method=(first_line.split()[0].upper() if first_line else None),
                    first_line=first_line[:240],
                    body_length=len(body),
                    call_id=self._first_header(headers, "call-id")[:160],
                    content_type=self._first_header(headers, "content-type")[:120],
                )
                self._record_sip_timeline("in", first_line, headers)
                if first_line.startswith("SIP/2.0 "):
                    code = self._status_code(first_line)
                    call_id = self._first_header(headers, "call-id")
                    cseq = self._first_header(headers, "cseq")
                    method = cseq.split()[-1].upper() if cseq else ""
                    if 100 <= code < 200:
                        self._trace_dispatcher(
                            "response_provisional",
                            method=method,
                            packet_id=packet_id,
                            status_code=code,
                        )
                        continue
                    future = self._pending.get((call_id, method))
                    if future is not None and not future.done():
                        future.set_result((raw, first_line, headers))
                    else:
                        _LOGGER.debug(
                            "Unmatched SIP response received: %s call-id=%s cseq=%s",
                            first_line,
                            call_id,
                            cseq,
                        )
                    self._trace_dispatcher(
                        "response_dispatched",
                        method=method,
                        packet_id=packet_id,
                        status_code=code,
                        matched=future is not None,
                    )
                    continue
                request_method = first_line.split()[0].upper() if first_line else None
                self._trace_dispatcher(
                    "request_dispatch_started",
                    method=request_method,
                    packet_id=packet_id,
                )
                try:
                    await self._async_handle_request(
                        session,
                        first_line,
                        headers,
                        body,
                        packet_id=packet_id,
                    )
                except Exception as err:
                    self._trace_dispatcher(
                        "request_dispatch_failed",
                        method=request_method,
                        packet_id=packet_id,
                        status="error",
                        error=f"{type(err).__name__}: {err}",
                    )
                    raise
                self._trace_dispatcher(
                    "request_dispatch_completed",
                    method=request_method,
                    packet_id=packet_id,
                )
        except asyncio.CancelledError:
            raise
        except (BticinoSipError, OSError, ssl.SSLError, TimeoutError) as err:
            self.last_error = str(err)
            _LOGGER.debug("BTicino SIP receive loop stopped: %s", err)
            if self._session is session:
                self.registered = False
                self.ringing = False
                self.call_state = "idle"
                self._notify("disconnected", server=self.server, port=self.port)
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(BticinoSipConnectionError(str(err)))

    def _record_sip_timeline(
        self,
        direction: str,
        first_line: str,
        headers: dict[str, list[str]],
    ) -> None:
        """Keep a bounded, non-secret SIP transaction timeline."""
        self.sip_timeline.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "session_id": self.runtime_session_id,
                "session_started_at": self.runtime_session_started_at.isoformat(),
                "direction": direction,
                "line": first_line[:240],
                "call_id": self._first_header(headers, "call-id")[:160],
                "cseq": self._first_header(headers, "cseq")[:80],
            }
        )

    async def _async_handle_request(
        self,
        session: SipSession,
        request_line: str,
        headers: dict[str, list[str]],
        body: bytes,
        *,
        packet_id: int | None = None,
    ) -> None:
        """Handle an unsolicited SIP request without taking over the call."""
        parts = request_line.split()
        if len(parts) < 3 or not parts[2].startswith("SIP/2.0"):
            self._trace_dispatcher(
                "request_rejected_malformed",
                packet_id=packet_id,
                status="error",
                request_line=request_line[:240],
            )
            _LOGGER.debug("Ignoring malformed SIP request: %s", request_line)
            return
        method = parts[0].upper()
        self.last_sip_method = method
        self._trace_dispatcher(
            "handler_entered",
            method=method,
            packet_id=packet_id,
            request_uri=parts[1],
            body_length=len(body),
        )
        call_id = self._first_header(headers, "call-id")
        from_value = self._first_header(headers, "from")

        if method == "INVITE":
            self.invite_received_count += 1
            self._trace_dispatcher(
                "invite_branch_entered",
                method=method,
                packet_id=packet_id,
                invite_received_count=self.invite_received_count,
            )
            self.last_dialog_headers = {
                "from": self._first_header(headers, "from"),
                "to": self._first_header(headers, "to"),
                "contact": self._first_header(headers, "contact"),
                "via": list(headers.get("via", [])),
                "record_route": list(headers.get("record-route", [])),
                "route": list(headers.get("route", [])),
                "content_type": self._first_header(headers, "content-type"),
                "call_id": call_id,
                "cseq": self._first_header(headers, "cseq"),
                "request_uri": parts[1] if len(parts) > 1 else "",
            }
            is_new_call = not self.ringing or (call_id and call_id != self._active_call_id)
            self._invite_headers = {name: list(values) for name, values in headers.items()}
            self._invite_request_uri = parts[1]
            self._invite_local_tag = self._tag()
            self.dialog_state = "early"
            self.invite_dispatched_count += 1
            self._trace_dispatcher(
                "invite_state_initialized",
                method=method,
                packet_id=packet_id,
                invite_dispatched_count=self.invite_dispatched_count,
                is_new_call=is_new_call,
            )
            if is_new_call:
                self._active_call_id = call_id or None
                self._notify(
                    "invite_received",
                    caller=from_value,
                    call_id=call_id,
                    request_uri=parts[1],
                    content_type=self._first_header(headers, "content-type"),
                    has_sdp=bool(
                        body
                        and "application/sdp" in self._first_header(headers, "content-type").lower()
                    ),
                    invite_received_count=self.invite_received_count,
                )
            self._start_media_trace(call_id or None)
            content_type = self._first_header(headers, "content-type").lower()
            self._trace_media(
                "invite_content_inspected",
                status="ok",
                content_type=content_type,
                body_length=len(body),
                has_sdp=bool(body and "application/sdp" in content_type),
            )
            if body and "application/sdp" in content_type:
                self.invite_with_sdp_count += 1
                self._trace_dispatcher(
                    "invite_sdp_detected",
                    method=method,
                    packet_id=packet_id,
                    invite_with_sdp_count=self.invite_with_sdp_count,
                    body_length=len(body),
                )
                self.last_sdp_offer = body.decode("utf-8", "replace")
                self._trace_media(
                    "sdp_extracted",
                    status="ok",
                    sdp_length=len(self.last_sdp_offer),
                )
                try:
                    description = self._parse_sdp(self.last_sdp_offer)
                except Exception as err:
                    self._trace_media(
                        "sdp_parse_failed",
                        status="error",
                        error=f"{type(err).__name__}: {err}",
                    )
                    raise
                self._trace_media(
                    "sdp_parsed",
                    status="ok",
                    media_sections=len(description.media),
                    session_address=description.connection_address,
                )
                try:
                    self._trace_dispatcher(
                        "media_runtime_call_started",
                        method=method,
                        packet_id=packet_id,
                    )
                    self._apply_sdp(description)
                    if self.media_plan is not None:
                        self.invite_media_runtime_count += 1
                    self._trace_dispatcher(
                        "media_runtime_call_completed",
                        method=method,
                        packet_id=packet_id,
                        runtime_state=self.media_runtime_state,
                        media_plan_available=self.media_plan is not None,
                        invite_media_runtime_count=self.invite_media_runtime_count,
                    )
                except Exception as err:
                    self._trace_media(
                        "media_runtime_update_failed",
                        status="error",
                        error=f"{type(err).__name__}: {err}",
                    )
                    _LOGGER.exception("Unable to update Media Runtime for INVITE")
            else:
                self._trace_media(
                    "sdp_not_available",
                    status="error",
                    error="INVITE does not contain an application/sdp body",
                )
            now = datetime.now(UTC)
            self.ringing = True
            self.call_state = "ringing"
            caller_identity = parse_sip_identity(from_value)
            self.last_caller = caller_identity.label if caller_identity else None
            self.last_caller_raw = caller_identity.raw if caller_identity else None
            self.last_caller_uri = caller_identity.uri if caller_identity else None
            self.last_caller_domain = caller_identity.domain if caller_identity else None
            self.last_caller_tag = caller_identity.tag if caller_identity else None
            self.last_caller_display_name = (
                caller_identity.display_name if caller_identity else None
            )
            self.last_call_id = call_id or self.last_call_id
            if is_new_call:
                self.call_started_at = now
                self.call_ended_at = None
                self.last_call_duration = None
                self.call_count += 1
                if self._call_timeout_task is not None:
                    self._call_timeout_task.cancel()
                self._call_timeout_task = asyncio.create_task(
                    self._async_call_timeout(call_id or "")
                )
            await self._async_send_response(session.writer, 100, "Trying", headers)
            await self._async_send_response(
                session.writer,
                180,
                "Ringing",
                headers,
                add_to_tag=True,
                to_tag=self._invite_local_tag,
            )
            event_data = {
                "caller": from_value,
                "call_id": call_id,
                "request_uri": parts[1],
                "started_at": self.call_started_at.isoformat() if self.call_started_at else None,
                "call_count": self.call_count,
                "content_type": self._first_header(headers, "content-type"),
                "has_sdp": self.last_sdp_offer is not None,
                "sdp_summary": self.last_sdp_summary,
                "audio_address": self.sdp_audio_address,
                "audio_port": self.sdp_audio_port,
                "audio_direction": self.sdp_audio_direction,
                "audio_codecs": list(self.sdp_audio_codecs),
                "video_address": self.sdp_video_address,
                "video_port": self.sdp_video_port,
                "video_direction": self.sdp_video_direction,
                "video_codecs": list(self.sdp_video_codecs),
                "media_preparation": self.media_preparation.public_dict()
                if self.media_preparation
                else None,
            }
            if is_new_call:
                self._notify("incoming_call", **event_data)
                self._notify("doorbell_pressed", **event_data)
            self._trace_dispatcher(
                "invite_branch_completed",
                method=method,
                packet_id=packet_id,
                has_sdp=bool(self.last_sdp_offer),
                runtime_state=self.media_runtime_state,
                media_plan_available=self.media_plan is not None,
            )
            return

        if method in {"CANCEL", "BYE"}:
            self._trace_dispatcher(
                "dialog_termination_branch_entered",
                method=method,
                packet_id=packet_id,
            )
            # CANCEL receives 200 OK for its own transaction. If the INVITE is
            # still early, terminate that INVITE transaction with 487 using
            # the same local To-tag established by the 180 Ringing response.
            await self._async_send_response(
                session.writer,
                200,
                "OK",
                headers,
                add_to_tag=True,
                to_tag=self._invite_local_tag,
            )
            if method == "CANCEL" and self._invite_headers is not None:
                await self._async_send_response(
                    session.writer,
                    487,
                    "Request Terminated",
                    self._invite_headers,
                    add_to_tag=True,
                    to_tag=self._invite_local_tag,
                )
            was_ringing = self.ringing
            now = datetime.now(UTC)
            if self._call_timeout_task is not None:
                self._call_timeout_task.cancel()
                self._call_timeout_task = None
            self._active_call_id = None
            self.ringing = False
            self.call_ended_at = now
            if self.call_started_at is not None:
                self.last_call_duration = max(0.0, (now - self.call_started_at).total_seconds())
            self.call_state = "missed" if method == "CANCEL" and was_ringing else "ended"
            self._notify(
                "call_ended",
                caller=from_value or self.last_caller,
                call_id=call_id or self.last_call_id,
                method=method,
                state=self.call_state,
                ended_at=now.isoformat(),
                duration_seconds=self.last_call_duration,
            )
            self.dialog_state = "terminated"
            self._clear_active_dialog(method.lower())
            if self.call_state == "missed":
                self.missed_call_count += 1
                self._notify(
                    "missed_call",
                    caller=from_value or self.last_caller,
                    call_id=call_id or self.last_call_id,
                    duration_seconds=self.last_call_duration,
                    missed_call_count=self.missed_call_count,
                )
            return

        if method == "MESSAGE":
            await self._async_send_response(session.writer, 200, "OK", headers, add_to_tag=True)
            cseq = self._first_header(headers, "cseq")
            message_key = (call_id, cseq)
            if message_key in self._recent_messages:
                return
            self._recent_messages.append(message_key)
            message = body.decode("utf-8", "replace")
            self.last_message = message
            self.last_message_at = datetime.now(UTC)
            self.message_count += 1
            self._notify(
                "message_received",
                caller=from_value,
                call_id=call_id,
                message=message,
                content_type=self._first_header(headers, "content-type"),
                received_at=self.last_message_at.isoformat(),
                message_count=self.message_count,
            )
            return

        if method == "OPTIONS":
            await self._async_send_response(session.writer, 200, "OK", headers, add_to_tag=True)
            return

        if method == "ACK":
            self.dialog_state = "confirmed"
            self._notify("sip_ack_received", caller=from_value, call_id=call_id)
            return

        if method == "INFO":
            await self._async_send_response(session.writer, 200, "OK", headers, add_to_tag=True)
            self.last_info_body = body.decode("utf-8", "replace")
            self._notify(
                "sip_info_received",
                caller=from_value,
                call_id=call_id,
                content_type=self._first_header(headers, "content-type"),
                body=self.last_info_body,
            )
            return

        if method == "NOTIFY":
            await self._async_send_response(session.writer, 200, "OK", headers, add_to_tag=True)
            self.last_notify_event = self._first_header(headers, "event")
            self._notify(
                "sip_notify_received",
                caller=from_value,
                call_id=call_id,
                event=self.last_notify_event,
                subscription_state=self._first_header(headers, "subscription-state"),
            )
            return

        if method == "REFER":
            await self._async_send_response(
                session.writer, 202, "Accepted", headers, add_to_tag=True
            )
            self.last_refer_to = self._first_header(headers, "refer-to")
            self._notify(
                "sip_refer_received",
                caller=from_value,
                call_id=call_id,
                refer_to=self.last_refer_to,
            )
            return

        if method in {"SUBSCRIBE", "PRACK", "UPDATE"}:
            await self._async_send_response(session.writer, 200, "OK", headers, add_to_tag=True)
            self._notify(
                "sip_request_received",
                method=method,
                caller=from_value,
                call_id=call_id,
            )
            return

        await self._async_send_response(
            session.writer, 501, "Not Implemented", headers, add_to_tag=True
        )

    @staticmethod
    def _parse_sdp(value: str) -> SdpDescription:
        """Parse the subset of SDP required for RTP negotiation diagnostics."""
        session_name: str | None = None
        session_address: str | None = None
        session_direction = "sendrecv"
        current: _SdpSection | None = None
        media_sections: list[_SdpSection] = []

        static_codecs = {
            0: "PCMU/8000",
            3: "GSM/8000",
            4: "G723/8000",
            8: "PCMA/8000",
            9: "G722/8000",
            18: "G729/8000",
            26: "JPEG/90000",
            31: "H261/90000",
            32: "MPV/90000",
            34: "H263/90000",
        }

        for raw_line in value.replace("\r", "").split("\n"):
            line = raw_line.strip()
            if len(line) < 2 or line[1] != "=":
                continue
            kind, data = line[0], line[2:].strip()
            if kind == "s":
                session_name = data or None
            elif kind == "c":
                address = data.split()[-1] if data else None
                if current is None:
                    session_address = address
                else:
                    current["address"] = address
            elif kind == "m":
                parts = data.split()
                if len(parts) < 4:
                    continue
                try:
                    port = int(parts[1].split("/", 1)[0])
                except ValueError:
                    port = 0
                payloads: list[int] = []
                for item in parts[3:]:
                    try:
                        payloads.append(int(item))
                    except ValueError:
                        continue
                current = {
                    "media": parts[0].lower(),
                    "port": port,
                    "protocol": parts[2],
                    "payloads": payloads,
                    "address": None,
                    "direction": session_direction,
                    "rtpmap": {},
                    "fmtp": {},
                    "crypto": [],
                    "rtcp_fb": {},
                }
                media_sections.append(current)
            elif kind == "a":
                if data in {"sendrecv", "sendonly", "recvonly", "inactive"}:
                    if current is None:
                        session_direction = data
                    else:
                        current["direction"] = data
                elif current is not None and data.startswith("rtpmap:"):
                    mapping = data[7:].split(None, 1)
                    if len(mapping) == 2:
                        try:
                            int_pt = int(mapping[0])
                        except ValueError:
                            continue
                        current["rtpmap"][int_pt] = mapping[1]
                elif current is not None and data.startswith("crypto:"):
                    offer = parse_crypto_attribute(data[7:])
                    if offer is not None:
                        current["crypto"].append(offer)
                elif current is not None and data.startswith("rtcp-fb:"):
                    mapping = data[8:].split(None, 1)
                    if mapping:
                        try:
                            int_pt = int(mapping[0])
                        except ValueError:
                            int_pt = -1
                        current["rtcp_fb"].setdefault(int_pt, []).append(
                            mapping[1] if len(mapping) == 2 else ""
                        )
                elif current is not None and data.startswith("fmtp:"):
                    mapping = data[5:].split(None, 1)
                    if mapping:
                        try:
                            int_pt = int(mapping[0])
                        except ValueError:
                            continue
                        current["fmtp"][int_pt] = mapping[1] if len(mapping) == 2 else ""

        parsed_media: list[SdpMediaDescription] = []
        for section in media_sections:
            codecs: list[str] = []
            for payload in section["payloads"]:
                codec = (
                    section["rtpmap"].get(payload) or static_codecs.get(payload) or f"PT{payload}"
                )
                codecs.append(f"{payload}:{codec}")
            parsed_media.append(
                SdpMediaDescription(
                    media=str(section["media"]),
                    port=int(section["port"]),
                    protocol=str(section["protocol"]),
                    payload_types=tuple(section["payloads"]),
                    connection_address=section["address"] or session_address,
                    direction=str(section["direction"]),
                    codecs=tuple(codecs),
                    fmtp=dict(section["fmtp"]),
                    crypto=tuple(section["crypto"]),
                    rtcp_feedback={int(k): tuple(v) for k, v in section["rtcp_fb"].items()},
                )
            )
        return SdpDescription(
            session_name=session_name,
            connection_address=session_address,
            direction=session_direction,
            media=tuple(parsed_media),
        )

    def _apply_sdp(self, description: SdpDescription) -> None:
        """Store parsed SDP details and emit a media-offer event."""
        self._trace_media(
            "apply_sdp_entered",
            status="ok",
            media_sections=len(description.media),
        )
        self.sdp_session_address = description.connection_address
        self.sdp_audio_address = None
        self.sdp_audio_port = None
        self.sdp_audio_direction = None
        self.sdp_audio_codecs = ()
        self.sdp_audio_protocol = None
        self.sdp_audio_payload_types = ()
        self.sdp_audio_fmtp = {}
        self.sdp_video_address = None
        self.sdp_video_port = None
        self.sdp_video_direction = None
        self.sdp_video_codecs = ()
        self.sdp_video_protocol = None
        self.sdp_video_payload_types = ()
        self.sdp_video_fmtp = {}

        summary_parts: list[str] = []
        for media in description.media:
            summary_parts.append(
                f"{media.media} {media.connection_address or '-'}:{media.port} "
                f"{media.direction} [{', '.join(media.codecs) or 'no codecs'}]"
            )
            if media.media == "audio" and self.sdp_audio_port is None:
                self.sdp_audio_address = media.connection_address
                self.sdp_audio_port = media.port
                self.sdp_audio_direction = media.direction
                self.sdp_audio_codecs = media.codecs
                self.sdp_audio_protocol = media.protocol
                self.sdp_audio_payload_types = media.payload_types
                self.sdp_audio_fmtp = dict(media.fmtp)
            elif media.media == "video" and self.sdp_video_port is None:
                self.sdp_video_address = media.connection_address
                self.sdp_video_port = media.port
                self.sdp_video_direction = media.direction
                self.sdp_video_codecs = media.codecs
                self.sdp_video_protocol = media.protocol
                self.sdp_video_payload_types = media.payload_types
                self.sdp_video_fmtp = dict(media.fmtp)

        self.last_sdp_summary = "; ".join(summary_parts) or "No RTP media sections"
        self._trace_media(
            "sdp_fields_stored",
            status="ok",
            summary=self.last_sdp_summary,
            audio_port=self.sdp_audio_port,
            video_port=self.sdp_video_port,
        )
        self._release_media_preparation()
        self.media_runtime_state = "preparing"
        self.media_runtime_call_id = self._active_call_id or self.last_call_id
        self.media_runtime_started_at = datetime.now(UTC)
        self.media_runtime_prepared_at = None
        self.media_runtime_closed_at = None
        self.last_media_remote_sdp = self.last_sdp_offer
        self.last_media_local_sdp = None
        self.last_media_sdp_diff = None
        self._notify(
            "media_remote_sdp_parsed",
            call_id=self.media_runtime_call_id,
            summary=self.last_sdp_summary,
        )
        self._trace_media("prepare_media_offer_called", status="ok")
        try:
            self.media_preparation = prepare_media_offer(description)
            self._trace_media(
                "media_preparation_created",
                status="ok",
                preparation_state=self.media_preparation.state,
                issue_count=len(self.media_preparation.issues),
            )
        except Exception as err:
            self.media_preparation = MediaPreparation(state="failed", issues=(str(err),))
            self._trace_media(
                "media_preparation_failed",
                status="error",
                error=f"{type(err).__name__}: {err}",
            )

        media_plan = self.media_preparation.public_dict() if self.media_preparation else None
        self.last_media_preparation = media_snapshot(self.media_preparation)
        self._trace_media(
            "runtime_snapshot_stored",
            status="ok" if self.last_media_preparation is not None else "error",
            snapshot_available=self.last_media_preparation is not None,
        )
        if self.media_preparation is not None:
            self.last_media_local_sdp = self.media_preparation.answer_sdp_redacted
            self.last_media_sdp_diff = build_sdp_diff(
                self.last_media_remote_sdp,
                self.last_media_local_sdp,
            )
            if self.media_preparation.state == "prepared":
                self.media_runtime_state = "prepared"
                self.media_runtime_prepared_at = datetime.now(UTC)
                self.media_trace_state = "prepared"
                self._trace_media(
                    "runtime_updated",
                    status="ok",
                    runtime_state=self.media_runtime_state,
                    ready_for_answer=self.media_runtime.get("ready_for_answer"),
                )
                self._notify(
                    "media_srtp_selected",
                    call_id=self.media_runtime_call_id,
                    suite=self.media_preparation.srtp_suite,
                    audio_codec=self.media_preparation.audio_codec,
                    video_codec=self.media_preparation.video_codec,
                )
                self._notify(
                    "media_local_sdp_generated",
                    call_id=self.media_runtime_call_id,
                    answer_sdp_fingerprint=self.media_preparation.answer_sdp_fingerprint,
                    local_media_address=self.media_preparation.local_media_address,
                )
                self._notify(
                    "media_session_prepared",
                    call_id=self.media_runtime_call_id,
                    prepared_at=self.media_runtime_prepared_at.isoformat(),
                    media_runtime=self.media_runtime,
                )
            else:
                self.media_runtime_state = "failed"
                self.media_trace_state = "failed"
                self._trace_media(
                    "runtime_updated",
                    status="error",
                    error="MediaPreparation did not reach prepared state",
                    issues=list(self.media_preparation.issues),
                )
                self._notify(
                    "media_session_failed",
                    call_id=self.media_runtime_call_id,
                    issues=list(self.media_preparation.issues),
                )
        self._notify(
            "sdp_offer_parsed",
            session_name=description.session_name,
            session_address=description.connection_address,
            session_direction=description.direction,
            summary=self.last_sdp_summary,
            audio_address=self.sdp_audio_address,
            audio_port=self.sdp_audio_port,
            audio_direction=self.sdp_audio_direction,
            audio_codecs=list(self.sdp_audio_codecs),
            audio_protocol=self.sdp_audio_protocol,
            audio_payload_types=list(self.sdp_audio_payload_types),
            audio_fmtp=dict(self.sdp_audio_fmtp),
            video_address=self.sdp_video_address,
            video_port=self.sdp_video_port,
            video_direction=self.sdp_video_direction,
            video_codecs=list(self.sdp_video_codecs),
            video_protocol=self.sdp_video_protocol,
            video_payload_types=list(self.sdp_video_payload_types),
            video_fmtp=dict(self.sdp_video_fmtp),
            media_preparation=media_plan,
        )

    async def _async_call_timeout(self, call_id: str) -> None:
        """Mark a ringing call as missed when no final SIP request arrives."""
        try:
            await asyncio.sleep(CALL_TIMEOUT_SECONDS)
            if not self.ringing or (call_id and self._active_call_id != call_id):
                return
            now = datetime.now(UTC)
            self.ringing = False
            self.call_state = "missed"
            self.call_ended_at = now
            self.last_call_duration = (
                max(0.0, (now - self.call_started_at).total_seconds())
                if self.call_started_at
                else None
            )
            self.missed_call_count += 1
            self.dialog_state = "terminated"
            self._clear_active_dialog("timeout")
            data = {
                "caller": self.last_caller,
                "call_id": self.last_call_id,
                "duration_seconds": self.last_call_duration,
                "missed_call_count": self.missed_call_count,
                "reason": "timeout",
            }
            self._notify("call_timeout", **data)
            self._notify("missed_call", **data)
        except asyncio.CancelledError:
            raise
        finally:
            if asyncio.current_task() is self._call_timeout_task:
                self._call_timeout_task = None

    async def _async_send_response(
        self,
        writer: asyncio.StreamWriter,
        code: int,
        reason: str,
        request_headers: dict[str, list[str]],
        *,
        add_to_tag: bool = False,
        to_tag: str | None = None,
    ) -> None:
        vias = request_headers.get("via", [])
        from_value = self._first_header(request_headers, "from")
        to_value = self._first_header(request_headers, "to")
        if add_to_tag and "tag=" not in to_value.lower():
            to_value = f"{to_value};tag={to_tag or self._tag()}"
        lines = [f"SIP/2.0 {code} {reason}"]
        lines.extend(f"Via: {value}" for value in vias)
        if from_value:
            lines.append(f"From: {from_value}")
        if to_value:
            lines.append(f"To: {to_value}")
        call_id = self._first_header(request_headers, "call-id")
        cseq = self._first_header(request_headers, "cseq")
        if call_id:
            lines.append(f"Call-ID: {call_id}")
        if cseq:
            lines.append(f"CSeq: {cseq}")
        lines.extend([f"User-Agent: {USER_AGENT}", "Content-Length: 0", "", ""])
        await self._async_write(writer, "\r\n".join(lines).encode())

    @staticmethod
    def _first_header(headers: dict[str, list[str]], name: str) -> str:
        values = headers.get(name.lower(), [])
        return values[0] if values else ""

    @classmethod
    async def _read_sip_frame(cls, reader: asyncio.StreamReader, timeout: float) -> bytes:  # noqa: ASYNC109 - Preserve the SIP timeout contract (including test doubles).
        """Read one SIP response or request, including its body."""
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError("Idle SIP stream timeout")
            try:
                header_block = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), remaining)
            except asyncio.IncompleteReadError as err:
                raise BticinoSipConnectionError("SIP connection closed") from err
            except TimeoutError:
                raise
            header_block = header_block.lstrip(b"\r\n")
            if not header_block:
                continue
            head = header_block[:-4]
            match = re.search(rb"(?im)^Content-Length:\s*(\d+)\s*$", head)
            length = int(match.group(1)) if match else 0
            body = b""
            if length:
                remaining = deadline - asyncio.get_running_loop().time()
                try:
                    body = await asyncio.wait_for(reader.readexactly(length), remaining)
                except (asyncio.IncompleteReadError, TimeoutError) as err:
                    raise BticinoSipConnectionError("Incomplete SIP frame body") from err
            return head + b"\r\n\r\n" + body

    @staticmethod
    def _parse_message(
        raw: bytes,
    ) -> tuple[str, dict[str, list[str]], bytes]:
        head, _, body = raw.partition(b"\r\n\r\n")
        lines = head.decode("utf-8", "replace").split("\r\n")
        first_line = lines[0] if lines else ""
        headers: dict[str, list[str]] = {}
        for line in lines[1:]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            headers.setdefault(key.strip().lower(), []).append(value.strip())
        return first_line, headers, body

    async def _read_final_response(
        self,
        reader: asyncio.StreamReader,
        timeout: int = 30,  # noqa: ASYNC109 - Preserve the SIP timeout contract (including test doubles).
    ) -> tuple[bytes, str, dict[str, list[str]]]:
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise BticinoSipConnectionError("Timeout waiting for final SIP response")
            raw = await self._read_response(reader, remaining)
            if self._debug is not None:
                self._debug.protocol("in", raw)
            status, headers = self._parse_headers(raw)
            code = self._status_code(status)
            if 100 <= code < 200:
                continue
            return raw, status, headers

    @staticmethod
    async def _read_response(reader: asyncio.StreamReader, timeout: float) -> bytes:  # noqa: ASYNC109 - Preserve the SIP timeout contract (including test doubles).
        """Read exactly one SIP response while preserving queued responses.

        ``StreamReader.readuntil`` leaves bytes belonging to a following SIP
        response in the internal buffer. Leading CRLF keepalive replies are
        discarded before parsing the status line.
        """
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise BticinoSipConnectionError("Timeout waiting for SIP response headers")
            try:
                header_block = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), remaining)
            except asyncio.IncompleteReadError as err:
                raise BticinoSipConnectionError(
                    "SIP server closed the connection before a complete response"
                ) from err
            except asyncio.LimitOverrunError as err:
                raise BticinoSipConnectionError("SIP response headers exceed stream limit") from err
            except TimeoutError as err:
                raise BticinoSipConnectionError("Timeout waiting for SIP response headers") from err

            # Flexisip may answer CRLF keepalives. Remove any number of leading
            # empty lines and continue if the frame contains no SIP status.
            header_block = header_block.lstrip(b"\r\n")
            if not header_block:
                continue
            if not header_block.startswith(b"SIP/2.0 "):
                _LOGGER.debug(
                    "Discarding non-SIP data received on BTicino stream: %r",
                    header_block[:120],
                )
                continue

            head = header_block[:-4]
            match = re.search(rb"(?im)^Content-Length:\s*(\d+)\s*$", head)
            length = int(match.group(1)) if match else 0
            body = b""
            if length:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    raise BticinoSipConnectionError("Timeout waiting for SIP response body")
                try:
                    body = await asyncio.wait_for(reader.readexactly(length), remaining)
                except (asyncio.IncompleteReadError, TimeoutError) as err:
                    raise BticinoSipConnectionError("Incomplete SIP response body") from err
            return head + b"\r\n\r\n" + body

    @staticmethod
    def _parse_headers(raw: bytes) -> tuple[str, dict[str, list[str]]]:
        text = raw.decode("utf-8", "replace")
        head = text.partition("\r\n\r\n")[0]
        lines = head.split("\r\n")
        status = lines[0] if lines else ""
        headers: dict[str, list[str]] = {}
        for line in lines[1:]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            headers.setdefault(key.strip().lower(), []).append(value.strip())
        return status, headers

    @staticmethod
    def _status_code(status: str) -> int:
        match = re.match(r"^SIP/2\.0\s+(\d{3})\b", status.strip())
        if not match:
            raise BticinoSipConnectionError(f"Invalid or stale SIP response status: {status!r}")
        return int(match.group(1))

    @staticmethod
    def _challenge(headers: dict[str, list[str]]) -> tuple[str, str]:
        if values := headers.get("www-authenticate"):
            return values[0], "Authorization"
        if values := headers.get("proxy-authenticate"):
            return values[0], "Proxy-Authorization"
        raise BticinoSipAuthenticationError("Authentication challenge missing")

    @staticmethod
    def _digest_params(value: str) -> dict[str, str]:
        value = re.sub(r"^\s*Digest\s+", "", value, flags=re.I)
        result: dict[str, str] = {}
        for match in re.finditer(r'(\w+)=("([^"]*)"|([^,\s]+))', value):
            result[match.group(1).lower()] = (
                match.group(3) if match.group(3) is not None else match.group(4)
            )
        return result

    @classmethod
    def _make_digest_auth(
        cls,
        challenge: str,
        method: str,
        uri: str,
        username: str,
        password: str,
        nc: int = 1,
    ) -> str:
        params = cls._digest_params(challenge)
        realm = params.get("realm", "")
        nonce = params.get("nonce", "")
        algorithm = params.get("algorithm", "MD5").upper()
        qops = [item.strip() for item in params.get("qop", "").split(",") if item.strip()]
        qop = "auth" if "auth" in qops else (qops[0] if qops else None)
        cnonce = secrets.token_hex(8)
        nc_text = f"{nc:08x}"

        def md5(value: str) -> str:
            return hashlib.md5(value.encode(), usedforsecurity=False).hexdigest()  # noqa: S324

        ha1 = md5(f"{username}:{realm}:{password}")
        if algorithm == "MD5-SESS":
            ha1 = md5(f"{ha1}:{nonce}:{cnonce}")
        elif algorithm != "MD5":
            raise BticinoSipAuthenticationError(f"Unsupported Digest algorithm: {algorithm}")
        ha2 = md5(f"{method}:{uri}")
        response = (
            md5(f"{ha1}:{nonce}:{nc_text}:{cnonce}:{qop}:{ha2}")
            if qop
            else md5(f"{ha1}:{nonce}:{ha2}")
        )
        parts = [
            f'username="{username}"',
            f'realm="{realm}"',
            f'nonce="{nonce}"',
            f'uri="{uri}"',
            f'response="{response}"',
            f"algorithm={algorithm}",
        ]
        if opaque := params.get("opaque"):
            parts.append(f'opaque="{opaque}"')
        if qop:
            parts.extend((f"qop={qop}", f"nc={nc_text}", f'cnonce="{cnonce}"'))
        return "Digest " + ", ".join(parts)

    @classmethod
    def _build_request(
        cls,
        *,
        method: str,
        request_uri: str,
        identity_uri: str,
        contact_uri: str,
        cseq: int,
        call_id: str,
        from_tag: str,
        route: str | None = None,
        auth_header: str | None = None,
        auth_name: str = "Authorization",
        body: str = "",
        content_type: str | None = None,
    ) -> bytes:
        headers = [
            f"{method} {request_uri} SIP/2.0",
            f"Via: SIP/2.0/TLS homeassistant.invalid;branch={cls._branch()};rport",
            "Max-Forwards: 70",
            f"From: <{identity_uri}>;tag={from_tag}",
            f"To: <{identity_uri if method == 'REGISTER' else request_uri}>",
            f"Call-ID: {call_id}",
            f"CSeq: {cseq} {method}",
            f"Contact: <{contact_uri}>",
            f"User-Agent: {USER_AGENT}",
            "Supported: outbound, path, gruu",
            "Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO",
        ]
        if route:
            headers.append(f"Route: <{route}>")
        if method == "REGISTER":
            headers.append(f"Expires: {DEFAULT_EXPIRES}")
        if auth_header:
            headers.append(f"{auth_name}: {auth_header}")
        if content_type:
            headers.append(f"Content-Type: {content_type}")
        body_bytes = body.encode()
        headers.append(f"Content-Length: {len(body_bytes)}")
        return ("\r\n".join(headers) + "\r\n\r\n").encode() + body_bytes

    @staticmethod
    def _branch() -> str:
        return "z9hG4bK" + secrets.token_hex(8)

    @staticmethod
    def _tag() -> str:
        return secrets.token_hex(6)

    @staticmethod
    def _call_id() -> str:
        return f"{uuid.uuid4()}@homeassistant"

    @staticmethod
    def _safe_preview(raw: bytes) -> str:
        text = raw.decode("utf-8", "replace")
        return re.sub(
            r"(?im)^(Authorization|Proxy-Authorization):.*$",
            r"\1: [REDACTED]",
            text,
        )[:1500]
