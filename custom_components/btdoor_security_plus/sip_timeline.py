"""Pure helpers for classifying persisted SIP timeline entries."""

from __future__ import annotations

from typing import Any

SIP_METHODS = frozenset(
    {
        "ACK",
        "BYE",
        "CANCEL",
        "INFO",
        "INVITE",
        "MESSAGE",
        "NOTIFY",
        "OPTIONS",
        "PRACK",
        "PUBLISH",
        "REFER",
        "REGISTER",
        "SUBSCRIBE",
        "UPDATE",
    }
)


def classify_timeline_event(event: dict[str, Any]) -> str:
    """Return a stable category for a persisted SIP timeline entry."""
    explicit = event.get("event") or event.get("type")
    if explicit and str(explicit).strip().lower() != "unknown":
        return str(explicit).strip()

    line = str(event.get("line") or "").strip()
    if line.upper().startswith("SIP/2.0 "):
        parts = line.split(maxsplit=2)
        if len(parts) >= 2 and parts[1].isdigit():
            status = int(parts[1])
            if 100 <= status <= 699:
                return f"{status // 100}xx"
        return "unknown"

    if line:
        method = line.split(maxsplit=1)[0].upper()
        if method in SIP_METHODS:
            return method

    cseq = str(event.get("cseq") or "").strip()
    if cseq:
        method = cseq.rsplit(maxsplit=1)[-1].upper()
        if method in SIP_METHODS:
            return method

    return "unknown"
