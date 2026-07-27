"""Immutable aggregate runtime models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .call import CallSnapshot
from .cloud import CloudSnapshot
from .media import MediaSnapshot
from .sip import SipSnapshot


@dataclass(frozen=True, slots=True)
class RuntimeCapabilities:
    """Capabilities available for the current configuration entry."""

    cloud: bool = True
    sip: bool = True
    gate_control: bool = True
    calls: bool = True
    media: bool = False
    developer_tools: bool = False
    support_bundle_v2: bool = False


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """Consistent immutable snapshot shared by diagnostics and dashboards."""

    lifecycle_state: str
    generated_at: str
    cloud: CloudSnapshot = field(default_factory=CloudSnapshot)
    sip: SipSnapshot = field(default_factory=SipSnapshot)
    call: CallSnapshot = field(default_factory=CallSnapshot)
    media: MediaSnapshot = field(default_factory=MediaSnapshot)
    capabilities: RuntimeCapabilities = field(default_factory=RuntimeCapabilities)
    last_error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return asdict(self)
