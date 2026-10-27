"""Stable Device Registry manager facade for the runtime architecture."""

from __future__ import annotations

from typing import Any

from ..device_model.factory import DeviceKind, device_identifier, device_info_for
from ..models.device import DeviceTopologyReport
from .device_name_provider import DeviceNameProvider
from .language_manager import LanguageManager


class DeviceManager:
    """Own registration and validation of the integration device topology."""

    def __init__(self, hass: Any, entry: Any) -> None:
        self.hass = hass
        self.entry = entry
        self.language_manager = LanguageManager.from_entry(entry)
        self.name_provider = DeviceNameProvider(self.language_manager)

    async def async_register(self) -> None:
        from ..device_model.manager import async_register_devices

        await async_register_devices(self.hass, self.entry)

    def report(self) -> dict[str, Any]:
        from ..device_model.manager import device_registry_report

        return device_registry_report(self.hass, self.entry)

    def validate_topology(self) -> DeviceTopologyReport:
        from homeassistant.helpers import device_registry as dr

        registry = dr.async_get(self.hass)
        missing: list[str] = []
        duplicates: list[str] = []
        mismatches: list[str] = []
        actual = 0
        user_names_preserved = True
        devices_with_area: list[str] = []
        devices_without_area: list[str] = []

        seen_ids: set[str] = set()
        for kind in DeviceKind:
            identifier = device_identifier(self.entry, kind)
            matches = [
                device
                for device in registry.devices.values()
                if identifier in device.identifiers and self.entry.entry_id in device.config_entries
            ]
            if not matches:
                missing.append(kind.value)
                continue
            actual += len(matches)
            if len(matches) > 1:
                duplicates.append(kind.value)
            expected = device_info_for(self.entry, kind)
            for device in matches:
                if device.id in seen_ids:
                    duplicates.append(kind.value)
                seen_ids.add(device.id)
                for field in ("manufacturer", "model", "sw_version"):
                    expected_value = expected.get(field)
                    if getattr(device, field, None) != expected_value:
                        mismatches.append(
                            f"{kind.value}.{field}: {getattr(device, field, None)!r} != {expected_value!r}"
                        )
                if kind not in {DeviceKind.GATEWAY, DeviceKind.VOICE_BRIDGE}:
                    root = registry.async_get_device(
                        identifiers={device_identifier(self.entry, DeviceKind.GATEWAY)}
                    )
                    if root is not None and device.via_device_id != root.id:
                        mismatches.append(f"{kind.value}.via_device")
                if getattr(device, "area_id", None) is not None:
                    devices_with_area.append(kind.value)
                else:
                    devices_without_area.append(kind.value)
                if device.name_by_user is not None and not device.name_by_user.strip():
                    user_names_preserved = False

        return DeviceTopologyReport(
            valid=not missing and not duplicates and not mismatches,
            expected_count=len(DeviceKind),
            actual_count=actual,
            missing_devices=tuple(sorted(set(missing))),
            duplicate_devices=tuple(sorted(set(duplicates))),
            metadata_mismatches=tuple(mismatches),
            user_names_preserved=user_names_preserved,
            automatic_areas_assigned=False,
            areas_left_unassigned=bool(devices_without_area),
            integration_assigns_areas=False,
            integration_suggested_areas=(),
            devices_with_area=tuple(sorted(set(devices_with_area))),
            devices_without_area=tuple(sorted(set(devices_without_area))),
        )


async def async_register_devices(hass: Any, entry: Any) -> None:
    """Compatibility entrypoint used by the integration lifecycle."""
    await DeviceManager(hass, entry).async_register()
