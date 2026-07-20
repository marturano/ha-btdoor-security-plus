"""Device registry lifecycle for BTDoor Security+."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers import device_registry as dr, entity_registry as er

from ..visibility import visibility_for_entry
from .factory import DeviceKind, device_identifier, device_info_for
from .names import device_name, normalize_language


async def async_register_devices(hass: Any, entry: Any) -> None:
    """Create visible devices, migrate managed names, and remove hidden modules."""
    registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    visibility = visibility_for_entry(entry)

    for kind in DeviceKind:
        if visibility.is_visible(kind):
            continue
        device = registry.async_get_device(identifiers={device_identifier(entry, kind)})
        if device is None:
            continue
        for entity in list(
            er.async_entries_for_device(
                entity_registry, device.id, include_disabled_entities=True
            )
        ):
            if entity.config_entry_id == entry.entry_id:
                entity_registry.async_remove(entity.entity_id)
        registry.async_remove_device(device.id)

    for kind in DeviceKind:
        if not visibility.is_visible(kind):
            continue
        info = device_info_for(entry, kind)
        device = registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers=info["identifiers"],
            manufacturer=info.get("manufacturer"),
            model=info.get("model"),
            name=info.get("name"),
            sw_version=info.get("sw_version"),
            configuration_url=info.get("configuration_url"),
            via_device=info.get("via_device"),
            serial_number=info.get("serial_number"),
        )
        # Home Assistant preserves the original registry name after creation.
        # Explicitly migrate only integration-managed names. A user-assigned
        # name always wins and is never overwritten.
        expected_name = info.get("name")
        updates: dict[str, Any] = {}
        if device.name_by_user is None and device.name != expected_name:
            updates["name"] = expected_name
        if device.manufacturer != info.get("manufacturer"):
            updates["manufacturer"] = info.get("manufacturer")
        if device.model != info.get("model"):
            updates["model"] = info.get("model")
        if device.sw_version != info.get("sw_version"):
            updates["sw_version"] = info.get("sw_version")
        if updates:
            registry.async_update_device(device.id, **updates)


def device_registry_report(hass: Any, entry: Any) -> dict[str, Any]:
    """Return a sanitized-ready report for devices owned by this entry."""
    registry = dr.async_get(hass)
    language = normalize_language(getattr(entry.runtime_data, "language", "en"))
    devices: list[dict[str, Any]] = []

    for kind in DeviceKind:
        device = registry.async_get_device(identifiers={device_identifier(entry, kind)})
        if device is None:
            continue
        expected = device_info_for(entry, kind)
        devices.append(
            {
                "kind": kind.value,
                "device_id": device.id,
                "display_name": device.name_by_user or device.name,
                "integration_name": device.name,
                "name_by_user": device.name_by_user,
                "expected_name": expected.get("name"),
                "name_matches_expected": device.name == expected.get("name"),
                "manufacturer": device.manufacturer,
                "model": device.model,
                "sw_version": device.sw_version,
                "configuration_url": device.configuration_url,
                "via_device_id": device.via_device_id,
            }
        )

    return {
        "schema_version": 1,
        "entry_id": entry.entry_id,
        "resolved_language": language,
        "device_count": len(devices),
        "devices": devices,
    }


def device_translation_report(entry: Any) -> dict[str, Any]:
    """Return the resolved logical-device translation catalog."""
    raw_language = str(getattr(entry.runtime_data, "language", "en") or "en")
    resolved = normalize_language(raw_language)
    names = {
        kind.value: device_name(kind, resolved)
        for kind in DeviceKind
        if kind is not DeviceKind.GATEWAY
    }
    raw_base = raw_language.strip().lower().replace("_", "-").split("-", 1)[0]
    return {
        "schema_version": 1,
        "home_assistant_language": raw_language,
        "integration_language_mode": "home_assistant",
        "resolved_language": resolved,
        "fallback_to_english": raw_base not in {"en", "it", "fr", "de", "es", "nl"},
        "device_names": names,
    }
