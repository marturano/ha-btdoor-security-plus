"""Manager APIs for the modular runtime architecture."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "DashboardManager": ("dashboard_manager", "DashboardManager"),
    "DeviceManager": ("device_manager", "DeviceManager"),
    "async_register_devices": ("device_manager", "async_register_devices"),
    "DeviceNameProvider": ("device_name_provider", "DeviceNameProvider"),
    "LanguageManager": ("language_manager", "LanguageManager"),
    "LanguageResolution": ("language_manager", "LanguageResolution"),
    "VisibilityManager": ("visibility_manager", "VisibilityManager"),
    "visibility_for_entry": ("visibility_manager", "visibility_for_entry"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    """Load manager APIs lazily to keep package imports side-effect free."""
    try:
        module_name, attribute = _EXPORTS[name]
    except KeyError as err:
        raise AttributeError(name) from err
    value = getattr(import_module(f"{__name__}.{module_name}"), attribute)
    globals()[name] = value
    return value
