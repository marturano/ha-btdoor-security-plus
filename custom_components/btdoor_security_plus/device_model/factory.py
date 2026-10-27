"""Central DeviceInfo factory for BTDoor Security+."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo

from ..const import (
    CONF_DEVICE_NAME,
    CONF_GATEWAY_ID,
    CONF_GATEWAY_NAME,
    CONF_ID_DEVICE,
    DOMAIN,
    INTEGRATION_VERSION,
)

MANUFACTURER = "BTicino / Legrand"
CONFIGURATION_URL = "https://github.com/marturano/ha-btdoor-security-plus"


class DeviceKind(StrEnum):
    """Logical devices exposed by one configuration entry."""

    GATEWAY = "gateway"
    CLOUD = "cloud"
    SIP = "sip"
    DIALOG = "dialog"
    MEDIA = "media"
    DIAGNOSTICS = "diagnostics"
    VOICE_BRIDGE = "voice_bridge"


def _root_key(entry: Any) -> str:
    """Return the stable per-entry key used by all identifiers."""
    return str(entry.unique_id or entry.data.get(CONF_ID_DEVICE) or entry.entry_id)


def device_identifier(entry: Any, kind: DeviceKind) -> tuple[str, str]:
    """Return one stable identifier for a logical device."""
    return (DOMAIN, f"{kind.value}_{_root_key(entry)}")


def gateway_identifiers(entry: Any) -> set[tuple[str, str]]:
    """Return gateway identifiers including the pre-Beta.2 legacy identifier."""
    identifiers = {device_identifier(entry, DeviceKind.GATEWAY)}
    id_device = str(entry.data.get(CONF_ID_DEVICE, "")).strip()
    if id_device:
        identifiers.add((DOMAIN, f"sip_client_{id_device}"))
    return identifiers


def _entry_language(entry: Any) -> str:
    """Return the Home Assistant language captured for this entry."""
    runtime_data = getattr(entry, "runtime_data", None)
    return str(getattr(runtime_data, "language", "en"))


def device_info_for(entry: Any, kind: DeviceKind) -> DeviceInfo:
    """Build consistent DeviceInfo for one logical runtime device."""
    root = device_identifier(entry, DeviceKind.GATEWAY)
    gateway_name = str(
        entry.data.get(CONF_GATEWAY_NAME) or entry.data.get(CONF_DEVICE_NAME) or "BTDoor Gateway"
    )
    models: dict[DeviceKind, str] = {
        DeviceKind.GATEWAY: "DS+ Suite - Integration Hub",
        DeviceKind.CLOUD: "DS+ Suite - Cloud Status",
        DeviceKind.SIP: "DS+ Suite - SIP Monitor",
        DeviceKind.DIALOG: "DS+ Suite - Call Manager",
        DeviceKind.MEDIA: "DS+ Suite - Multimedia Monitor",
        DeviceKind.DIAGNOSTICS: "DS+ Suite - Advanced Diagnostics",
        DeviceKind.VOICE_BRIDGE: "Alexa / Google Gate Bridge",
    }
    if kind is DeviceKind.GATEWAY:
        name = gateway_name
    else:
        # Local import avoids coupling the base device model to localization
        # during package initialization.
        from .names import device_name

        name = device_name(kind, _entry_language(entry)) or kind.value
    model = models[kind]
    identifiers = (
        gateway_identifiers(entry)
        if kind is DeviceKind.GATEWAY
        else {device_identifier(entry, kind)}
    )
    info = DeviceInfo(
        identifiers=identifiers,
        name=name,
        manufacturer=MANUFACTURER,
        model=model,
        sw_version=INTEGRATION_VERSION,
        configuration_url=CONFIGURATION_URL,
    )
    if kind not in {DeviceKind.GATEWAY, DeviceKind.VOICE_BRIDGE}:
        info["via_device"] = root
    gateway_id = entry.data.get(CONF_GATEWAY_ID)
    if kind is DeviceKind.GATEWAY and gateway_id:
        info["serial_number"] = str(gateway_id)
    return info
