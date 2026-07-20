"""SIP dialog session model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .dialog_state import DialogState


@dataclass(slots=True)
class DialogSession:
    """State and identifiers for one SIP dialog."""

    call_id: str
    local_tag: str | None = None
    remote_tag: str | None = None
    state: DialogState = DialogState.IDLE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "local_tag": self.local_tag,
            "remote_tag": self.remote_tag,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": dict(self.metadata),
        }
