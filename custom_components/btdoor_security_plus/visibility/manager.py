"""Central device visibility policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..const import (
    CONF_DEVELOPER_MODE,
    CONF_QUICK_VOICE_GATE,
    CONF_SHOW_ADVANCED_DIAGNOSTICS,
    CONF_SHOW_CALL_MONITOR,
    CONF_SHOW_CLOUD_STATUS,
    CONF_SHOW_MEDIA_MONITOR,
    CONF_SHOW_SIP_MONITOR,
    DEFAULT_DEVELOPER_MODE,
    DEFAULT_QUICK_VOICE_GATE,
    DEFAULT_SHOW_ADVANCED_DIAGNOSTICS,
    DEFAULT_SHOW_CALL_MONITOR,
    DEFAULT_SHOW_CLOUD_STATUS,
    DEFAULT_SHOW_MEDIA_MONITOR,
    DEFAULT_SHOW_SIP_MONITOR,
)
from ..device_model.factory import DeviceKind


@dataclass(frozen=True, slots=True)
class DeviceVisibilityManager:
    """Resolve which logical devices and entities are exposed to Home Assistant."""

    cloud: bool = DEFAULT_SHOW_CLOUD_STATUS
    sip: bool = DEFAULT_SHOW_SIP_MONITOR
    calls: bool = DEFAULT_SHOW_CALL_MONITOR
    media: bool = DEFAULT_SHOW_MEDIA_MONITOR
    diagnostics: bool = False
    voice_bridge: bool = DEFAULT_QUICK_VOICE_GATE

    @classmethod
    def from_entry(cls, entry: Any) -> DeviceVisibilityManager:
        options = entry.options
        developer_mode = bool(options.get(CONF_DEVELOPER_MODE, DEFAULT_DEVELOPER_MODE))
        return cls(
            cloud=bool(options.get(CONF_SHOW_CLOUD_STATUS, DEFAULT_SHOW_CLOUD_STATUS)),
            sip=bool(options.get(CONF_SHOW_SIP_MONITOR, DEFAULT_SHOW_SIP_MONITOR)),
            calls=bool(options.get(CONF_SHOW_CALL_MONITOR, DEFAULT_SHOW_CALL_MONITOR)),
            media=bool(options.get(CONF_SHOW_MEDIA_MONITOR, DEFAULT_SHOW_MEDIA_MONITOR)),
            diagnostics=(
                developer_mode
                and bool(
                    options.get(CONF_SHOW_ADVANCED_DIAGNOSTICS, DEFAULT_SHOW_ADVANCED_DIAGNOSTICS)
                )
            ),
            voice_bridge=bool(options.get(CONF_QUICK_VOICE_GATE, DEFAULT_QUICK_VOICE_GATE)),
        )

    def is_visible(self, kind: DeviceKind) -> bool:
        if kind is DeviceKind.GATEWAY:
            return True
        return {
            DeviceKind.CLOUD: self.cloud,
            DeviceKind.SIP: self.sip,
            DeviceKind.DIALOG: self.calls,
            DeviceKind.MEDIA: self.media,
            DeviceKind.DIAGNOSTICS: self.diagnostics,
            DeviceKind.VOICE_BRIDGE: self.voice_bridge,
        }[kind]

    def filter_entities(self, entities: list[Any]) -> list[Any]:
        return [entity for entity in entities if self.is_visible(entity._device_kind)]

    def as_dict(self) -> dict[str, bool]:
        return {
            "cloud_status": self.cloud,
            "sip_monitor": self.sip,
            "call_monitor": self.calls,
            "media_monitor": self.media,
            "advanced_diagnostics": self.diagnostics,
            "voice_bridge": self.voice_bridge,
        }


def visibility_for_entry(entry: Any) -> DeviceVisibilityManager:
    return DeviceVisibilityManager.from_entry(entry)
