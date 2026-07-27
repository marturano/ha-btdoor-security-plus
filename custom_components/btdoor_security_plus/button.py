"""Developer buttons for BTDoor Security+."""
from __future__ import annotations

import json

from homeassistant.components.button import ButtonEntity
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


# Push-driven platform; entity updates do not perform parallel device I/O.
PARALLEL_UPDATES = 0

from .entity import BticinoDoorEntryEntity
from .const import (
    ATTR_ENTRY_ID, ATTR_REASON, ATTR_SOURCE, CONF_QUICK_VOICE_GATE,
    DEFAULT_QUICK_VOICE_GATE, DOMAIN, SERVICE_OPEN_GATE,
)
from .device_model import DeviceKind
from .visibility import visibility_for_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    entities = [BTDoorGateOpenButton(entry)]
    if visibility_for_entry(entry).is_visible(DeviceKind.DIAGNOSTICS):
        entities.extend([
            BTDoorDeveloperTestButton(entry),
            BTDoorSupportReportButton(entry),
            BTDoorCleanDebugButton(entry),
        ])
    async_add_entities(entities)


class BTDoorGateOpenButton(BticinoDoorEntryEntity, ButtonEntity):
    """Momentary gate opener suitable for Home Assistant and voice routines."""

    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "open_gate"
    _attr_icon = "mdi:gate-open"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_open_gate_button"

    @property
    def available(self) -> bool:
        return getattr(self._entry, "runtime_data", None) is not None

    @property
    def extra_state_attributes(self) -> dict[str, bool]:
        return {
            "quick_voice_assistants_enabled": bool(
                self._entry.options.get(
                    CONF_QUICK_VOICE_GATE, DEFAULT_QUICK_VOICE_GATE
                )
            )
        }

    async def async_press(self) -> None:
        response = await self.hass.services.async_call(
            DOMAIN,
            SERVICE_OPEN_GATE,
            {
                ATTR_ENTRY_ID: self._entry.entry_id,
                ATTR_REASON: "Gate button command",
                ATTR_SOURCE: "button",
            },
            blocking=True,
            return_response=True,
            context=self._context,
        )
        result = (response or {}).get(self._entry.entry_id, {})
        if not result.get("success"):
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="gate_open_failed",
                translation_placeholders={
                    "error": result.get("error") or "BTicino gate opening failed"
                },
            )


class _DeveloperButton(BticinoDoorEntryEntity, ButtonEntity):
    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        return bool(self._entry.runtime_data.developer and self._entry.runtime_data.developer.enabled)


class BTDoorDeveloperTestButton(_DeveloperButton):
    _attr_translation_key = "run_developer_test"
    _attr_icon = "mdi:flask-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_run_developer_test"

    async def async_press(self) -> None:
        results = await self._entry.runtime_data.developer.async_run_tests("all")
        failed = [name for name, item in results.items() if not item.get("ok")]
        title = "BTDoor Security+ - Test sviluppatore"
        message = "Tutti i test sono riusciti." if not failed else f"Test non riusciti: {', '.join(failed)}"
        persistent_notification.async_create(self.hass, message, title=title, notification_id=f"btdoor_dev_test_{self._entry.entry_id}")
        self.async_write_ha_state()


class BTDoorSupportReportButton(_DeveloperButton):
    _attr_translation_key = "generate_support_report"
    _attr_icon = "mdi:file-document-arrow-right-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_generate_support_report"

    async def async_press(self) -> None:
        result = await self._entry.runtime_data.developer.async_generate_support_report(True)
        persistent_notification.async_create(
            self.hass,
            f"Report creato.\n\nMarkdown: `{result['report_path']}`\n\nZIP: `{result['bundle_path']}`",
            title="BTDoor Security+ - Report di Supporto",
            notification_id=f"btdoor_support_report_{self._entry.entry_id}",
        )
        self.async_write_ha_state()


class BTDoorCleanDebugButton(_DeveloperButton):
    _attr_translation_key = "clean_debug_environment"
    _attr_icon = "mdi:broom"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_clean_debug_environment"

    async def async_press(self) -> None:
        result = await self._entry.runtime_data.developer.async_clean_debug_environment()
        persistent_notification.async_create(
            self.hass,
            f"Ambiente di debug pulito. File rimossi: {result['removed_files']}.",
            title="BTDoor Security+ - Pulizia debug",
            notification_id=f"btdoor_clean_debug_{self._entry.entry_id}",
        )
        self.async_write_ha_state()
