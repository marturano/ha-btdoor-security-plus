"""Redacted support diagnostics recorder for BTDoor Security+."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .const import (
    DEBUG_LOG_BACKUP_COUNT,
    DEBUG_LOG_MAX_BYTES,
    DEBUG_MODE_DEEP,
    DEBUG_MODE_OFF,
    DEBUG_RECENT_RECORDS,
)

_SENSITIVE_KEYS = {
    "password",
    "sip_password",
    "auth_token",
    "authorization",
    "proxy-authorization",
    "nonce",
    "response",
    "client_key",
    "private_key",
    "csr",
    "cookie",
    "set-cookie",
}
_AUTH_RE = re.compile(r"(?im)^(authorization|proxy-authorization):.*$")
_EMAIL_RE = re.compile(r"(?i)([a-z0-9._%+-]{1,3})[a-z0-9._%+-]*@([a-z0-9.-]+)")
_TOKEN_RE = re.compile(r"(?i)(auth_token|password|sip_password|nonce|response)=([^,;\s]+)")
_PEM_RE = re.compile(r"-----BEGIN [^-]+-----.*?-----END [^-]+-----", re.S)
_CRYPTO_INLINE_RE = re.compile(r"(?im)(^a=crypto:[^\r\n]*?\sinline:)([^|;\s\r\n]+)")
_IPV4_RE = re.compile(r"(?<![\d.])((?:\d{1,3}\.){3}\d{1,3})(?![\d.])")

_SIP_CALL_ID_RE = re.compile(r"(?im)(^(?:call-id|i):\s*)([^\r\n]+)$")
_SIP_BRANCH_RE = re.compile(r"(?i)(branch=)([^;\s,>]+)")
_SIP_TAG_RE = re.compile(r"(?i)(;tag=)([\"\']?)([^;\s,>\"\']+)(?:[\"\']?)")
_SIP_INSTANCE_RE = re.compile(r"(?i)(sip\.instance\s*=\s*)(?:\"([^\"]+)\"|([^;\s,]+))")


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:12]


def redact_text(value: str) -> str:
    """Remove credentials and minimize personal data from debug text."""
    value = _PEM_RE.sub("[REDACTED PEM]", value)
    value = _AUTH_RE.sub(lambda m: f"{m.group(1)}: [REDACTED]", value)
    value = _TOKEN_RE.sub(lambda m: f"{m.group(1)}=[HASH:{_hash(m.group(2))}]", value)
    value = _EMAIL_RE.sub(lambda m: f"{m.group(1)}***@{m.group(2)}", value)
    value = _CRYPTO_INLINE_RE.sub(lambda m: f"{m.group(1)}[REDACTED]", value)
    return value


def redact_support_text(value: str) -> str:
    """Redact secrets and partially mask IP addresses for exported reports."""
    value = redact_text(value)

    def _mask_ip(match: re.Match[str]) -> str:
        parts = match.group(1).split(".")
        if len(parts) != 4 or any(not part.isdigit() or int(part) > 255 for part in parts):
            return match.group(1)
        return f"{parts[0]}.{parts[1]}.xxx.xxx"

    value = _IPV4_RE.sub(_mask_ip, value)
    value = _SIP_CALL_ID_RE.sub(lambda m: f"{m.group(1)}[HASH:{_hash(m.group(2))}]", value)
    value = _SIP_BRANCH_RE.sub(lambda m: f"{m.group(1)}[HASH:{_hash(m.group(2))}]", value)
    value = _SIP_TAG_RE.sub(lambda m: f"{m.group(1)}[HASH:{_hash(m.group(3))}]", value)
    value = _SIP_INSTANCE_RE.sub(
        lambda m: f'{m.group(1)}"[HASH:{_hash(m.group(2) or m.group(3))}]"', value
    )
    return value


def redact(value: Any, key: str | None = None) -> Any:
    if key and key.lower() in _SENSITIVE_KEYS:
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, bytes):
        return redact_text(value.decode("utf-8", "replace"))
    if isinstance(value, str):
        return redact_text(value)
    return value


class SupportDebugRecorder:
    """Asynchronous, size-limited, redacted JSONL support recorder."""

    def __init__(self, log_dir: Path, mode: str) -> None:
        self.mode = mode
        self.log_dir = log_dir
        self.log_path = log_dir / "support-debug.jsonl"
        self._queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(maxsize=1000)
        self._task: asyncio.Task[None] | None = None
        self._recent: deque[dict[str, Any]] = deque(maxlen=DEBUG_RECENT_RECORDS)
        self.dropped_records = 0

    @property
    def enabled(self) -> bool:
        return self.mode != DEBUG_MODE_OFF

    @property
    def deep(self) -> bool:
        return self.mode == DEBUG_MODE_DEEP

    async def async_start(self) -> None:
        if not self.enabled or self._task is not None:
            return
        await asyncio.to_thread(self.log_dir.mkdir, parents=True, exist_ok=True)
        self._task = asyncio.create_task(self._writer(), name="btdoor-support-debug")
        self.record("integration", "debug_started", mode=self.mode)

    async def async_stop(self) -> None:
        if self._task is None:
            return
        self.record("integration", "debug_stopping")
        await self._queue.put(None)
        await self._task
        self._task = None

    def record(self, category: str, event: str, **data: Any) -> None:
        if not self.enabled:
            return
        item = {
            "timestamp": datetime.now(UTC).isoformat(),
            "category": category,
            "event": event,
            "data": redact(data),
        }
        self._recent.append(item)
        try:
            self._queue.put_nowait(item)
        except asyncio.QueueFull:
            self.dropped_records += 1

    def protocol(self, direction: str, payload: bytes | str) -> None:
        if not self.deep:
            return
        text = payload.decode("utf-8", "replace") if isinstance(payload, bytes) else payload
        self.record("sip", "protocol_frame", direction=direction, frame=redact_text(text))

    def recent(self) -> list[dict[str, Any]]:
        return list(self._recent)

    async def async_clear(self) -> None:
        """Clear rotated debug files and in-memory records."""
        await asyncio.to_thread(self._clear_files)
        self._recent.clear()
        self.dropped_records = 0

    def _clear_files(self) -> None:
        for candidate in self.log_dir.glob("support-debug*.jsonl*"):
            candidate.unlink(missing_ok=True)

    async def _writer(self) -> None:
        while True:
            item = await self._queue.get()
            if item is None:
                return
            line = json.dumps(item, ensure_ascii=False, default=str) + "\n"
            await asyncio.to_thread(self._append_rotating, line)

    def _append_rotating(self, line: str) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if (
            self.log_path.exists()
            and self.log_path.stat().st_size + len(line.encode()) > DEBUG_LOG_MAX_BYTES
        ):
            oldest = self.log_path.with_suffix(f".jsonl.{DEBUG_LOG_BACKUP_COUNT}")
            oldest.unlink(missing_ok=True)
            for index in range(DEBUG_LOG_BACKUP_COUNT - 1, 0, -1):
                source = self.log_path.with_suffix(f".jsonl.{index}")
                if source.exists():
                    source.replace(self.log_path.with_suffix(f".jsonl.{index + 1}"))
            self.log_path.replace(self.log_path.with_suffix(".jsonl.1"))
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
