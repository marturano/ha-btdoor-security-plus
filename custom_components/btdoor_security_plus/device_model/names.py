"""Localized logical device names for BTDoor Security+."""
from __future__ import annotations

from typing import Final

from .factory import DeviceKind

DEFAULT_LANGUAGE: Final = "en"
SUPPORTED_LANGUAGES: Final = frozenset({"en", "it", "fr", "de", "es", "nl"})

_DEVICE_NAMES: Final[dict[str, dict[DeviceKind, str]]] = {
    "en": {
        DeviceKind.CLOUD: "Cloud Status",
        DeviceKind.SIP: "SIP Monitor",
        DeviceKind.DIALOG: "Call Manager",
        DeviceKind.MEDIA: "Multimedia Monitor",
        DeviceKind.DIAGNOSTICS: "Advanced Diagnostics",
    },
    "it": {
        DeviceKind.CLOUD: "Stato Cloud",
        DeviceKind.SIP: "Monitor SIP",
        DeviceKind.DIALOG: "Monitor Chiamate",
        DeviceKind.MEDIA: "Monitor Multimediale",
        DeviceKind.DIAGNOSTICS: "Diagnostica Avanzata",
    },
    "fr": {
        DeviceKind.CLOUD: "État du Cloud",
        DeviceKind.SIP: "Moniteur SIP",
        DeviceKind.DIALOG: "Gestionnaire d’appels",
        DeviceKind.MEDIA: "Moniteur multimédia",
        DeviceKind.DIAGNOSTICS: "Diagnostic avancé",
    },
    "de": {
        DeviceKind.CLOUD: "Cloud-Status",
        DeviceKind.SIP: "SIP-Monitor",
        DeviceKind.DIALOG: "Anrufmanager",
        DeviceKind.MEDIA: "Multimedia-Monitor",
        DeviceKind.DIAGNOSTICS: "Erweiterte Diagnose",
    },
    "es": {
        DeviceKind.CLOUD: "Estado de la nube",
        DeviceKind.SIP: "Monitor SIP",
        DeviceKind.DIALOG: "Gestor de llamadas",
        DeviceKind.MEDIA: "Monitor multimedia",
        DeviceKind.DIAGNOSTICS: "Diagnóstico avanzado",
    },
    "nl": {
        DeviceKind.CLOUD: "Cloudstatus",
        DeviceKind.SIP: "SIP-monitor",
        DeviceKind.DIALOG: "Oproepbeheer",
        DeviceKind.MEDIA: "Multimediamonitor",
        DeviceKind.DIAGNOSTICS: "Geavanceerde diagnostiek",
    },
}


def normalize_language(language: str | None) -> str:
    """Return a supported two-letter language code, falling back to English."""
    normalized = str(language or DEFAULT_LANGUAGE).strip().lower().replace("_", "-").split("-", 1)[0]
    return normalized if normalized in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def device_name(kind: DeviceKind, language: str | None) -> str | None:
    """Return the localized name for a logical device.

    The physical gateway keeps its user-configured name and therefore has no
    entry in this catalog.
    """
    if kind is DeviceKind.GATEWAY:
        return None
    return _DEVICE_NAMES[normalize_language(language)][kind]
