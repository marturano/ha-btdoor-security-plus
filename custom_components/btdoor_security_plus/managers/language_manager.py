"""Central language resolution for BTDoor Security+."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

DEFAULT_LANGUAGE: Final = "en"
SUPPORTED_LANGUAGES: Final = ("en", "it", "fr", "de", "es", "nl")
SUPPORTED_LANGUAGE_SET: Final = frozenset(SUPPORTED_LANGUAGES)


def normalize_language(language: str | None) -> str:
    """Normalize a locale to a supported two-letter language code."""
    normalized = (
        str(language or DEFAULT_LANGUAGE).strip().lower().replace("_", "-").split("-", 1)[0]
    )
    return normalized if normalized in SUPPORTED_LANGUAGE_SET else DEFAULT_LANGUAGE


@dataclass(frozen=True, slots=True)
class LanguageResolution:
    """Resolved language and fallback metadata."""

    requested: str
    resolved: str
    fallback_to_english: bool
    fallback_chain: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "requested": self.requested,
            "resolved": self.resolved,
            "fallback_to_english": self.fallback_to_english,
            "fallback_chain": list(self.fallback_chain),
        }


class LanguageManager:
    """Resolve the active integration language from Home Assistant."""

    def __init__(self, language: str | None) -> None:
        requested = str(language or DEFAULT_LANGUAGE).strip() or DEFAULT_LANGUAGE
        base = requested.lower().replace("_", "-").split("-", 1)[0]
        resolved = normalize_language(requested)
        chain = (resolved,) if resolved == DEFAULT_LANGUAGE else (resolved, DEFAULT_LANGUAGE)
        self._resolution = LanguageResolution(
            requested=requested,
            resolved=resolved,
            fallback_to_english=base not in SUPPORTED_LANGUAGE_SET,
            fallback_chain=chain,
        )

    @classmethod
    def from_entry(cls, entry: object) -> LanguageManager:
        runtime_data = getattr(entry, "runtime_data", None)
        return cls(getattr(runtime_data, "language", DEFAULT_LANGUAGE))

    @property
    def active_language(self) -> str:
        return self._resolution.resolved

    @property
    def resolution(self) -> LanguageResolution:
        return self._resolution

    def as_dict(self) -> dict[str, object]:
        return {
            "supported_languages": list(SUPPORTED_LANGUAGES),
            **self._resolution.as_dict(),
        }
