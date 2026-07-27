"""Immutable device topology models for BTDoor Security+."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DeviceDescriptor:
    """Stable metadata describing one integration device."""

    key: str
    name_key: str
    model: str
    manufacturer: str = "BTicino / Legrand"
    identifiers: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    via_device: tuple[str, str] | None = None
    suggested_area: None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DeviceTopologyReport:
    """Validation result for the expected Device Registry topology."""

    valid: bool
    expected_count: int
    actual_count: int
    missing_devices: tuple[str, ...] = field(default_factory=tuple)
    duplicate_devices: tuple[str, ...] = field(default_factory=tuple)
    metadata_mismatches: tuple[str, ...] = field(default_factory=tuple)
    user_names_preserved: bool = True
    automatic_areas_assigned: bool = False
    areas_left_unassigned: bool = True
    integration_assigns_areas: bool = False
    integration_suggested_areas: tuple[str, ...] = field(default_factory=tuple)
    devices_with_area: tuple[str, ...] = field(default_factory=tuple)
    devices_without_area: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""
        return asdict(self)
