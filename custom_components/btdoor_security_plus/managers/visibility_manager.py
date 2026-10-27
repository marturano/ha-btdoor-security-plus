"""Stable 6.1 facade for the device visibility policy."""

from __future__ import annotations

from ..visibility.manager import DeviceVisibilityManager, visibility_for_entry

VisibilityManager = DeviceVisibilityManager

__all__ = ["VisibilityManager", "visibility_for_entry"]
