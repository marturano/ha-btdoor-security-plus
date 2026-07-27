"""Resolve dashboard entities from stable integration unique IDs."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class DashboardEntityMap:
    """Resolved entity IDs used by the native dashboards."""

    open_gate: str | None = None
    sip_registered: str | None = None
    cloud_connected: str | None = None
    ringing: str | None = None
    call_state: str | None = None
    last_caller: str | None = None
    last_gate_open: str | None = None
    runtime_score: str | None = None
    runtime_healthy: str | None = None
    certificate_expiry: str | None = None
    door_entry_event: str | None = None
    developer_runtime_inspector: str | None = None
    developer_event_monitor: str | None = None
    developer_event_metrics: str | None = None
    run_developer_test: str | None = None
    generate_support_report: str | None = None
    clean_debug_environment: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return asdict(self)


_SUFFIXES: dict[str, str] = {
    "open_gate": "_open_gate_button",
    "sip_registered": "_sip_registered",
    "cloud_connected": "_cloud_connected",
    "ringing": "_ringing",
    "call_state": "_call_state",
    "last_caller": "_last_caller",
    "last_gate_open": "_last_gate_open",
    "runtime_score": "_runtime_score",
    "runtime_healthy": "_runtime_healthy",
    "certificate_expiry": "_certificate_expiry",
    "door_entry_event": "_event",
    "developer_runtime_inspector": "_developer_runtime_inspector",
    "developer_event_monitor": "_developer_event_monitor",
    "developer_event_metrics": "_developer_event_metrics",
    "run_developer_test": "_run_developer_test",
    "generate_support_report": "_generate_support_report",
    "clean_debug_environment": "_clean_debug_environment",
}


class DashboardEntityResolver:
    """Resolve entities without relying on user-editable entity IDs."""

    @staticmethod
    def resolve(entries: Iterable[Any], *, config_entry_id: str | None = None) -> DashboardEntityMap:
        resolved: dict[str, str | None] = {key: None for key in _SUFFIXES}
        for entry in entries:
            if config_entry_id is not None and getattr(entry, "config_entry_id", None) != config_entry_id:
                continue
            unique_id = str(getattr(entry, "unique_id", "") or "")
            entity_id = getattr(entry, "entity_id", None)
            if not entity_id:
                continue
            for key, suffix in _SUFFIXES.items():
                if unique_id.endswith(suffix):
                    resolved[key] = str(entity_id)
        return DashboardEntityMap(**resolved)

    @staticmethod
    def missing(entity_map: DashboardEntityMap, required: Iterable[str]) -> tuple[str, ...]:
        values = entity_map.as_dict()
        return tuple(key for key in required if not values.get(key))
