"""Event entity for BTDoor Security+."""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import BticinoConfigEntry
from .device_model import DeviceKind
from .entity import BticinoDoorEntryEntity

EVENT_TYPES = [
    "registered",
    "connection_restored",
    "disconnected",
    "gate_opened",
    "gate_open_failed",
    "incoming_call",
    "doorbell_pressed",
    "call_ended",
    "call_timeout",
    "missed_call",
    "message_received",
    "statistics_reset",
]

# Push-driven platform; entity updates do not perform parallel device I/O.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BticinoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([BticinoDoorEntryEvent(entry)])


class BticinoDoorEntryEvent(BticinoDoorEntryEntity, EventEntity):
    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "door_entry_event"
    _attr_event_types = EVENT_TYPES
    _attr_icon = "mdi:doorbell-video"

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_event"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self._entry.runtime_data.client.add_listener(self._handle_event))

    def _handle_event(self, event_type: str, data: dict[str, object]) -> None:
        if event_type in self._attr_event_types:
            self._trigger_event(event_type, data)
            self.async_write_ha_state()
