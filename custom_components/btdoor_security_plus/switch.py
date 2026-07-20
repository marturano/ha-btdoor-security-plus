"""Momentary gate control for BTDoor Security+ and Alexa/Alexa+."""

from __future__ import annotations

import asyncio

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import BticinoConfigEntry
from .entity import BticinoDoorEntryEntity
from .device_model import DeviceKind
from .sip_client import BticinoSipError


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BticinoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the single gate control entity."""
    async_add_entities([BticinoOpenGateSwitch(entry)])


class BticinoOpenGateSwitch(BticinoDoorEntryEntity, SwitchEntity):
    _device_kind = DeviceKind.GATEWAY
    """Single momentary gate control exposed to Home Assistant and Alexa."""

    _attr_translation_key = "open_gate"
    _attr_icon = "mdi:gate-open"
    _attr_is_on = False

    def __init__(self, entry: BticinoConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_open_gate_switch"

    async def async_turn_on(self, **kwargs) -> None:
        """Open the gate, then return immediately to off."""
        self._attr_is_on = True
        self.async_write_ha_state()
        try:
            result = await self._entry.runtime_data.client.async_open_gate()
            self._entry.runtime_data.last_result = result.status
        except BticinoSipError as err:
            self._entry.runtime_data.last_result = str(err)
            raise HomeAssistantError(f"BTicino gate opening failed: {err}") from err
        finally:
            self._attr_is_on = False
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Keep the momentary switch off."""
        self._attr_is_on = False
        self.async_write_ha_state()
