"""Dashboard manager for native Lovelace templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..ux import DashboardBuilder, DashboardEntityResolver


class DashboardManager:
    """Resolve registry entities and render native dashboard YAML."""

    def __init__(self, hass: Any, entry: Any, template_dir: Path) -> None:
        self.hass = hass
        self.entry = entry
        self.builder = DashboardBuilder(template_dir)

    def resolve_entities(self):
        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(self.hass)
        return DashboardEntityResolver.resolve(
            registry.entities.values(),
            config_entry_id=self.entry.entry_id,
        )

    def build(self, template_name: str):
        return self.builder.build(template_name, self.resolve_entities())
