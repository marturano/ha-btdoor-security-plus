"""Optional voice-assistant bridge switches for BTDoor Security+."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    ATTR_ENTRY_ID,
    ATTR_REASON,
    ATTR_SOURCE,
    CONF_QUICK_VOICE_GATE,
    DEFAULT_QUICK_VOICE_GATE,
    DOMAIN,
    SERVICE_OPEN_GATE,
)
from .device_model import DeviceKind
from .entity import BticinoDoorEntryEntity

if TYPE_CHECKING:
    from .service_models import GateActionResult

# Push-driven platform; entity updates do not perform parallel device I/O.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the optional Alexa/Google gate bridge."""
    if not entry.options.get(CONF_QUICK_VOICE_GATE, DEFAULT_QUICK_VOICE_GATE):
        return
    async_add_entities([BTDoorGateVoiceBridgeSwitch(entry)])


class BTDoorGateVoiceBridgeSwitch(BticinoDoorEntryEntity, SwitchEntity):
    """Stateless switch bridge displayed as a controllable Alexa device.

    Turning the entity on sends one gate-opening impulse. The entity never
    remains on, because the physical gate does not expose a persistent state.
    """

    _device_kind = DeviceKind.VOICE_BRIDGE
    _attr_translation_key = "open_gate_voice_bridge"
    _attr_icon = "mdi:gate-arrow-right"
    _attr_is_on = False

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_open_gate_voice_bridge"

    @property
    def available(self) -> bool:
        return getattr(self._entry, "runtime_data", None) is not None

    async def async_turn_on(self, **kwargs) -> None:
        response = await self.hass.services.async_call(
            DOMAIN,
            SERVICE_OPEN_GATE,
            {
                ATTR_ENTRY_ID: self._entry.entry_id,
                ATTR_REASON: "Voice-assistant bridge command",
                ATTR_SOURCE: "voice_bridge_switch",
            },
            blocking=True,
            return_response=True,
            context=self._context,
        )
        result = cast("GateActionResult", (response or {}).get(self._entry.entry_id, {}))
        if not result.get("success"):
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="gate_open_failed",
                translation_placeholders={
                    "error": result.get("error") or "BTicino gate opening failed"
                },
            )
        # Keep the bridge stateless. Alexa will show the control returning to off.
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Ignore turn-off: the gate command is a momentary impulse."""
        self._attr_is_on = False
        self.async_write_ha_state()
