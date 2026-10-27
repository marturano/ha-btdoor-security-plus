"""Localized logical-device names."""

from __future__ import annotations

from typing import Final

from ..device_model.factory import DeviceKind
from .language_manager import LanguageManager, normalize_language

_DEVICE_NAMES: Final[dict[str, dict[DeviceKind, str]]] = {
    "en": {
        DeviceKind.CLOUD: "Cloud Status",
        DeviceKind.SIP: "SIP Monitor",
        DeviceKind.DIALOG: "Call Manager",
        DeviceKind.MEDIA: "Multimedia Monitor",
        DeviceKind.DIAGNOSTICS: "Advanced Diagnostics",
        DeviceKind.VOICE_BRIDGE: "Gate Voice Bridge",
    },
    "it": {
        DeviceKind.CLOUD: "Stato Cloud",
        DeviceKind.SIP: "Monitor SIP",
        DeviceKind.DIALOG: "Monitor Chiamate",
        DeviceKind.MEDIA: "Monitor Multimediale",
        DeviceKind.DIAGNOSTICS: "Diagnostica Avanzata",
        DeviceKind.VOICE_BRIDGE: "Bridge vocale cancello",
    },
    "fr": {
        DeviceKind.CLOUD: "État du Cloud",
        DeviceKind.SIP: "Moniteur SIP",
        DeviceKind.DIALOG: "Gestionnaire d’appels",
        DeviceKind.MEDIA: "Moniteur multimédia",
        DeviceKind.DIAGNOSTICS: "Diagnostic avancé",
        DeviceKind.VOICE_BRIDGE: "Passerelle vocale du portail",
    },
    "de": {
        DeviceKind.CLOUD: "Cloud-Status",
        DeviceKind.SIP: "SIP-Monitor",
        DeviceKind.DIALOG: "Anrufmanager",
        DeviceKind.MEDIA: "Multimedia-Monitor",
        DeviceKind.DIAGNOSTICS: "Erweiterte Diagnose",
        DeviceKind.VOICE_BRIDGE: "Sprach-Bridge Tor",
    },
    "es": {
        DeviceKind.CLOUD: "Estado de la nube",
        DeviceKind.SIP: "Monitor SIP",
        DeviceKind.DIALOG: "Gestor de llamadas",
        DeviceKind.MEDIA: "Monitor multimedia",
        DeviceKind.DIAGNOSTICS: "Diagnóstico avanzado",
        DeviceKind.VOICE_BRIDGE: "Puente de voz del portón",
    },
    "nl": {
        DeviceKind.CLOUD: "Cloudstatus",
        DeviceKind.SIP: "SIP-monitor",
        DeviceKind.DIALOG: "Oproepbeheer",
        DeviceKind.MEDIA: "Multimediamonitor",
        DeviceKind.DIAGNOSTICS: "Geavanceerde diagnostiek",
        DeviceKind.VOICE_BRIDGE: "Spraakbridge poort",
    },
}


class DeviceNameProvider:
    """Return stable localized names for logical devices."""

    def __init__(self, language: LanguageManager | str | None) -> None:
        self._language = (
            language.active_language
            if isinstance(language, LanguageManager)
            else normalize_language(language)
        )

    @property
    def language(self) -> str:
        return self._language

    def name_for(self, kind: DeviceKind) -> str | None:
        if kind is DeviceKind.GATEWAY:
            return None
        return _DEVICE_NAMES[self._language][kind]

    def catalog(self) -> dict[str, str]:
        return {kind.value: name for kind, name in _DEVICE_NAMES[self._language].items()}
