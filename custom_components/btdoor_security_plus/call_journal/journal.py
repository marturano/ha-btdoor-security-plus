"""Persistent call journal derived exclusively from Runtime Event Bus events."""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from typing import Any, cast

from homeassistant.helpers.storage import Store

from ..event_bus import RuntimeEvent, RuntimeEventType


def _call_id(event: RuntimeEvent) -> str | None:
    value = event.payload.get("call_id")
    return str(value) if value else None


def _iso_duration(started: str | None, ended: str | None) -> float | None:
    if not started or not ended:
        return None
    try:
        return max(
            0.0, (datetime.fromisoformat(ended) - datetime.fromisoformat(started)).total_seconds()
        )
    except (TypeError, ValueError):
        return None


class CallJournal:
    """Maintain a bounded persistent call journal from normalized events."""

    def __init__(self, store: Store[dict[str, Any]], *, max_records: int = 250) -> None:
        self._store = store
        self._records: deque[dict[str, Any]] = deque(maxlen=max_records)
        self._active: dict[str, dict[str, Any]] = {}
        self._unsubscribe = None

    async def async_load(self) -> None:
        stored = await self._store.async_load() or {}
        for item in stored.get("records", []):
            if isinstance(item, dict):
                self._records.append(dict(item))
        active = stored.get("active") or {}
        if isinstance(active, dict):
            completed_ids = {
                str(item.get("call_id")) for item in self._records if item.get("call_id")
            }
            for key, value in active.items():
                if not isinstance(value, dict):
                    continue
                call_id = str(key)
                candidate = dict(value)
                # Self-heal storage produced by older builds: an entry with an end
                # timestamp is completed and must never be restored as active.
                if candidate.get("ended_at"):
                    if call_id not in completed_ids:
                        self._records.append(candidate)
                        completed_ids.add(call_id)
                    continue
                if call_id not in completed_ids:
                    self._active[call_id] = candidate

    def attach(self, event_bus) -> None:
        if self._unsubscribe is None:
            self._unsubscribe = event_bus.subscribe(self.process)

    def detach(self) -> None:
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None

    def process(self, event: RuntimeEvent) -> None:
        call_id = _call_id(event)
        if not call_id:
            return
        record = self._active.get(call_id)
        if event.event_type in (RuntimeEventType.INVITE_RECEIVED, RuntimeEventType.CALL_STARTED):
            if record is None:
                record = {
                    "schema_version": 1,
                    "call_id": call_id,
                    "direction": "incoming",
                    "started_at": event.timestamp,
                    "ended_at": None,
                    "caller": event.payload.get("caller"),
                    "result": "ringing",
                    "duration_seconds": None,
                    "close_reason": None,
                    "audio_codec": None,
                    "video_codec": None,
                    "srtp_suite": None,
                }
                self._active[call_id] = record
            elif not record.get("caller") and event.payload.get("caller"):
                record["caller"] = event.payload.get("caller")
        elif record is None:
            # Ignore late/duplicate events for a call that was already finalized.
            # Some gateways emit MISSED_CALL after MEDIA_CLOSED; older builds
            # recreated such calls as active, inflating active_calls forever.
            if self._is_completed(call_id):
                return
            # Only lifecycle events capable of describing an in-progress call may
            # create a fallback record. Terminal or auxiliary events alone may not.
            if event.event_type not in (
                RuntimeEventType.MEDIA_PREPARED,
                RuntimeEventType.MEDIA_OPENED,
                RuntimeEventType.CALL_ANSWERED,
            ):
                return
            record = {
                "schema_version": 1,
                "call_id": call_id,
                "direction": "incoming",
                "started_at": event.timestamp,
                "ended_at": None,
                "caller": None,
                "result": "unknown",
                "duration_seconds": None,
                "close_reason": None,
                "audio_codec": None,
                "video_codec": None,
                "srtp_suite": None,
            }
            self._active[call_id] = record

        if event.event_type == RuntimeEventType.MEDIA_PREPARED:
            media = event.payload.get("media_runtime") or {}
            plan = media.get("plan") if isinstance(media, dict) else {}
            plan = plan if isinstance(plan, dict) else {}
            audio = (
                cast(dict[str, Any], plan.get("audio"))
                if isinstance(plan.get("audio"), dict)
                else {}
            )
            video = (
                cast(dict[str, Any], plan.get("video"))
                if isinstance(plan.get("video"), dict)
                else {}
            )
            srtp = (
                cast(dict[str, Any], plan.get("srtp")) if isinstance(plan.get("srtp"), dict) else {}
            )
            record["audio_codec"] = audio.get("codec") or record.get("audio_codec")
            record["video_codec"] = video.get("codec") or record.get("video_codec")
            record["srtp_suite"] = srtp.get("suite") or record.get("srtp_suite")
        elif event.event_type == RuntimeEventType.CALL_ANSWERED:
            record["result"] = "answered"
        elif event.event_type == RuntimeEventType.CALL_REJECTED:
            record["result"] = "rejected"
            record["close_reason"] = "rejected"
        elif event.event_type == RuntimeEventType.CALL_CANCELLED:
            if record.get("result") != "answered":
                record["result"] = "missed"
            record["close_reason"] = str(event.payload.get("method") or "cancel").lower()
        elif event.event_type == RuntimeEventType.MEDIA_FAILED:
            record["result"] = "failed"
            record["close_reason"] = str(event.payload.get("error") or "media_failed")
            self._finalize(call_id, event.timestamp)
        elif event.event_type == RuntimeEventType.MEDIA_CLOSED:
            runtime = event.payload.get("media_runtime") or {}
            if isinstance(runtime, dict):
                record["ended_at"] = runtime.get("closed_at") or event.timestamp
                record["close_reason"] = runtime.get("close_reason") or record.get("close_reason")
                plan = (
                    cast(dict[str, Any], runtime.get("plan"))
                    if isinstance(runtime.get("plan"), dict)
                    else {}
                )
                audio = (
                    cast(dict[str, Any], plan.get("audio"))
                    if isinstance(plan.get("audio"), dict)
                    else {}
                )
                video = (
                    cast(dict[str, Any], plan.get("video"))
                    if isinstance(plan.get("video"), dict)
                    else {}
                )
                srtp = (
                    cast(dict[str, Any], plan.get("srtp"))
                    if isinstance(plan.get("srtp"), dict)
                    else {}
                )
                record["audio_codec"] = audio.get("codec") or record.get("audio_codec")
                record["video_codec"] = video.get("codec") or record.get("video_codec")
                record["srtp_suite"] = srtp.get("suite") or record.get("srtp_suite")
            self._finalize(call_id, str(record.get("ended_at") or event.timestamp))
        elif event.event_type == RuntimeEventType.CALL_ENDED:
            self._finalize(call_id, event.timestamp)

        self._store.async_delay_save(self.export_state, 1.0)

    def _is_completed(self, call_id: str) -> bool:
        """Return whether a call id is already present in completed records."""
        return any(str(record.get("call_id")) == call_id for record in self._records)

    def _finalize(self, call_id: str, ended_at: str) -> None:
        record = self._active.pop(call_id, None)
        if record is None:
            return
        record["ended_at"] = ended_at
        record["duration_seconds"] = round(
            _iso_duration(record.get("started_at"), ended_at) or 0.0, 3
        )
        if record.get("result") in ("ringing", "unknown"):
            record["result"] = "completed"
        self._records.append(record)

    async def async_clear(self) -> None:
        """Clear completed and active records and persist immediately."""
        self._records.clear()
        self._active.clear()
        await self._store.async_save(self.export_state())

    async def async_rebuild(self, events: list[RuntimeEvent]) -> None:
        """Rebuild the journal deterministically from retained runtime events."""
        self._records.clear()
        self._active.clear()
        for event in events:
            self.process(event)
        await self._store.async_save(self.export_state())

    @property
    def records(self) -> list[dict[str, Any]]:
        return list(self._records)

    @property
    def last_record(self) -> dict[str, Any] | None:
        return dict(self._records[-1]) if self._records else None

    @property
    def metrics(self) -> dict[str, Any]:
        results: dict[str, int] = {}
        durations: list[float] = []
        codecs: dict[str, int] = {}
        for record in self._records:
            result = str(record.get("result") or "unknown")
            results[result] = results.get(result, 0) + 1
            duration = record.get("duration_seconds")
            if isinstance(duration, (int, float)):
                durations.append(float(duration))
            codec = record.get("audio_codec")
            if codec:
                codecs[str(codec)] = codecs.get(str(codec), 0) + 1
        today = datetime.now(UTC).date()
        answered_today = 0
        missed_today = 0
        for record in self._records:
            stamp = record.get("started_at")
            try:
                record_date = datetime.fromisoformat(str(stamp)).date()
            except (TypeError, ValueError):
                continue
            if record_date == today:
                answered_today += int(record.get("result") == "answered")
                missed_today += int(record.get("result") == "missed")
        return {
            "schema_version": 1,
            "retained_calls": len(self._records),
            "active_calls": len(self._active),
            "calls_by_result": results,
            "average_duration_seconds": round(sum(durations) / len(durations), 3)
            if durations
            else None,
            "audio_codec_usage": codecs,
            "answered_today": answered_today,
            "missed_today": missed_today,
            "last_call": self.last_record,
        }

    def export_state(self) -> dict[str, Any]:
        return {"schema_version": 1, "records": self.records, "active": self._active}
