"""Device model for BTDoor Security+."""

from __future__ import annotations

from typing import Any

from .factory import DeviceKind, device_info_for


async def async_register_devices(hass: Any, entry: Any) -> None:
    """Register logical devices without importing lifecycle code at package import time."""
    from .manager import async_register_devices as _async_register_devices

    await _async_register_devices(hass, entry)


__all__ = ["DeviceKind", "async_register_devices", "device_info_for"]
