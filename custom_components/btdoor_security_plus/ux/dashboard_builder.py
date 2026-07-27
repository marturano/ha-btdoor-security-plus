"""Build native Lovelace YAML from tokenized templates."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .entity_resolver import DashboardEntityMap


@dataclass(frozen=True, slots=True)
class DashboardBuildResult:
    name: str
    content: str
    missing_entities: tuple[str, ...]


_TOKENS: dict[str, tuple[str, ...]] = {
    "open_gate": ("button.apri_cancello", "__ENTITY_OPEN_GATE__"),
    "sip_registered": ("binary_sensor.btdoor_template_sip_registered", "__ENTITY_SIP_REGISTERED__"),
    "cloud_connected": ("binary_sensor.btdoor_template_cloud_connected", "__ENTITY_CLOUD_CONNECTED__"),
    "ringing": ("binary_sensor.btdoor_template_ringing", "__ENTITY_RINGING__"),
    "call_state": ("sensor.btdoor_template_call_state", "__ENTITY_CALL_STATE__"),
    "last_caller": ("sensor.btdoor_template_last_caller", "__ENTITY_LAST_CALLER__"),
    "last_gate_open": ("sensor.btdoor_template_last_gate_open", "__ENTITY_LAST_GATE_OPEN__"),
    "runtime_score": ("sensor.btdoor_template_runtime_score", "__ENTITY_RUNTIME_SCORE__"),
    "runtime_healthy": ("binary_sensor.btdoor_template_runtime_healthy", "__ENTITY_RUNTIME_HEALTHY__"),
    "door_entry_event": ("event.btdoor_template_door_entry_event", "__ENTITY_DOOR_ENTRY_EVENT__"),
    "developer_runtime_inspector": ("sensor.btdoor_template_developer_runtime_inspector", "__ENTITY_DEVELOPER_RUNTIME_INSPECTOR__"),
    "developer_event_monitor": ("sensor.btdoor_template_developer_event_monitor", "__ENTITY_DEVELOPER_EVENT_MONITOR__"),
    "developer_event_metrics": ("sensor.btdoor_template_developer_event_metrics", "__ENTITY_DEVELOPER_EVENT_METRICS__"),
    "run_developer_test": ("button.btdoor_template_run_developer_test", "__ENTITY_RUN_DEVELOPER_TEST__"),
    "generate_support_report": ("button.btdoor_template_generate_support_report", "__ENTITY_GENERATE_SUPPORT_REPORT__"),
    "clean_debug_environment": ("button.btdoor_template_clean_debug_environment", "__ENTITY_CLEAN_DEBUG_ENVIRONMENT__"),
}


class DashboardBuilder:
    """Render dashboard templates using resolved entity IDs."""

    def __init__(self, template_dir: Path) -> None:
        self._template_dir = template_dir

    @staticmethod
    def _replace_tokens(value: Any, replacements: dict[str, str]) -> Any:
        """Recursively replace dashboard tokens in every YAML value.

        Replacements are intentionally applied to all strings, including deeply
        nested service targets, conditions and lists. Dictionary keys are also
        processed to avoid leaving an unresolved token in advanced card syntax.
        """
        if isinstance(value, str):
            for token, replacement in replacements.items():
                value = value.replace(token, replacement)
            return value
        if isinstance(value, list):
            return [DashboardBuilder._replace_tokens(item, replacements) for item in value]
        if isinstance(value, tuple):
            return tuple(DashboardBuilder._replace_tokens(item, replacements) for item in value)
        if isinstance(value, dict):
            return {
                DashboardBuilder._replace_tokens(key, replacements): DashboardBuilder._replace_tokens(item, replacements)
                for key, item in value.items()
            }
        return value

    def build(self, template_name: str, entities: DashboardEntityMap) -> DashboardBuildResult:
        path = self._template_dir / template_name
        source = path.read_text(encoding="utf-8")
        document = yaml.safe_load(source)
        values = entities.as_dict()
        missing: list[str] = []
        replacements: dict[str, str] = {}

        for key, tokens in _TOKENS.items():
            value = values.get(key)
            replacement = value or f"sensor.btdoor_missing_{key}"
            if not value and any(token in source for token in tokens):
                missing.append(key)
            for token in tokens:
                replacements[token] = replacement

        rendered = self._replace_tokens(document, replacements)
        content = yaml.safe_dump(rendered, sort_keys=False, allow_unicode=True)
        return DashboardBuildResult(template_name, content, tuple(missing))
