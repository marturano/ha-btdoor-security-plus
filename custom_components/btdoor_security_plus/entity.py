"""Base entities for BTDoor Security+."""

from __future__ import annotations

from homeassistant.helpers.entity import Entity

from . import BticinoConfigEntry
from .device_model import DeviceKind, device_info_for


class BticinoDoorEntryEntity(Entity):
    """Base entity attached to a logical BTDoor device."""

    _attr_has_entity_name = True
    _device_kind = DeviceKind.GATEWAY

    def __init__(self, entry: BticinoConfigEntry) -> None:
        self._entry = entry
        self._attr_device_info = device_info_for(entry, self._device_kind)


class BticinoSipClientEntity(BticinoDoorEntryEntity):
    """Compatibility base for SIP diagnostic entities."""

    _device_kind = DeviceKind.SIP
