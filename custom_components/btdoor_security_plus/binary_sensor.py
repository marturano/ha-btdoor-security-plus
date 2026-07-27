"""Binary sensors for BTDoor Security+."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


# Push-driven platform; entity updates do not perform parallel device I/O.
PARALLEL_UPDATES = 0

from . import BticinoConfigEntry
from .entity import BticinoDoorEntryEntity, BticinoSipClientEntity
from .device_model import DeviceKind
from .visibility import visibility_for_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BticinoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up diagnostics binary sensor."""
    entities = [
        BticinoSipRegisteredSensor(entry),
        BticinoRingingSensor(entry),
        BTDoorMediaReadySensor(entry),
        BTDoorLastCallMissedSensor(entry),
        BTDoorCloudConnectedSensor(entry),
        BTDoorDialogCallActiveSensor(entry),
    ]
    entities.append(BTDoorRuntimeHealthySensor(entry))
    async_add_entities(visibility_for_entry(entry).filter_entities(entities))


class BticinoSipRegisteredSensor(BticinoSipClientEntity, BinarySensorEntity):
    _device_kind = DeviceKind.SIP
    """Show whether a SIP operation is currently registered."""

    _attr_translation_key = "sip_registered"
    _attr_icon = "mdi:phone-check"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: BticinoConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_sip_registered"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self._entry.runtime_data.client.add_listener(
                lambda _event, _data: self.async_write_ha_state()
            )
        )

    @property
    def is_on(self) -> bool:
        """Return current registration state."""
        return self._entry.runtime_data.client.registered

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return diagnostic status."""
        return {"last_sip_status": self._entry.runtime_data.client.last_status}


class BticinoRingingSensor(BticinoDoorEntryEntity, BinarySensorEntity):
    _device_kind = DeviceKind.DIALOG
    """Show whether an incoming Door Entry call is ringing."""

    _attr_translation_key = "ringing"
    _attr_icon = "mdi:doorbell-video"

    def __init__(self, entry: BticinoConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_ringing"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self._entry.runtime_data.client.add_listener(
                lambda _event, _data: self.async_write_ha_state()
            )
        )

    @property
    def is_on(self) -> bool:
        return self._entry.runtime_data.client.ringing

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        client = self._entry.runtime_data.client
        return {"caller": client.last_caller, "call_id": client.last_call_id}


class BTDoorMediaReadySensor(BticinoSipClientEntity, BinarySensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "media_ready"
    _attr_icon = "mdi:multimedia"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: BticinoConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_media_ready"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self._entry.runtime_data.client.add_listener(lambda _event, _data: self.async_write_ha_state()))

    @property
    def is_on(self) -> bool:
        return self._entry.runtime_data.client.media_runtime_state == "prepared"


class BTDoorLastCallMissedSensor(BticinoDoorEntryEntity, BinarySensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_call_missed"
    _attr_icon = "mdi:phone-missed"

    def __init__(self, entry: BticinoConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_last_call_missed"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self._entry.runtime_data.client.add_listener(lambda _event, _data: self.async_write_ha_state()))

    @property
    def is_on(self) -> bool:
        client = self._entry.runtime_data.client
        session = client.last_completed_media_session or {}
        return str(session.get("closed_reason") or client.call_state or "").lower() in {"cancel", "missed"}


class BTDoorRuntimeHealthySensor(BticinoSipClientEntity, BinarySensorEntity):
    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_translation_key = "runtime_healthy"
    _attr_icon = "mdi:check-decagram"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: BticinoConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_runtime_healthy"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self._entry.runtime_data.client.add_listener(lambda _event, _data: self.async_write_ha_state()))

    @property
    def is_on(self) -> bool:
        client = self._entry.runtime_data.client
        return bool(client.registered and not client.last_error and client.media_runtime_state != "failed")


class BTDoorCloudConnectedSensor(BticinoSipClientEntity, BinarySensorEntity):
    _device_kind = DeviceKind.CLOUD
    _attr_translation_key = "cloud_connected"
    _attr_icon = "mdi:cloud-check"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_cloud_connected"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(self._entry.runtime_data.client.add_listener(lambda _event, _data: self.async_write_ha_state()))

    @property
    def is_on(self):
        return self._entry.runtime_data.api.cloud().connected


class BTDoorDialogCallActiveSensor(BticinoDoorEntryEntity, BinarySensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "dialog_call_active"
    _attr_icon = "mdi:phone-in-talk"

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_dialog_call_active"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(self._entry.runtime_data.client.add_listener(lambda _event, _data: self.async_write_ha_state()))

    @property
    def is_on(self):
        state = self._entry.runtime_data.api.dialog().state
        return state not in {"idle", "terminated", "closed"}
