"""Compatibility wrappers for localized logical-device names."""
from __future__ import annotations

from ..managers.device_name_provider import DeviceNameProvider
from ..managers.language_manager import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGE_SET as SUPPORTED_LANGUAGES,
    normalize_language,
)
from .factory import DeviceKind


def device_name(kind: DeviceKind, language: str | None) -> str | None:
    """Return the localized name through the localized device-name provider."""
    return DeviceNameProvider(language).name_for(kind)


__all__ = [
    "DEFAULT_LANGUAGE",
    "SUPPORTED_LANGUAGES",
    "device_name",
    "normalize_language",
]
