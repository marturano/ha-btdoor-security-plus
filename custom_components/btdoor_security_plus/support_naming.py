"""Naming helpers for BTDoor Security+ support artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SUPPORT_ARTIFACT_PREFIX = "BTDoorSecurityPlus_Support"
LEGACY_SUPPORT_ARTIFACT_PREFIXES: tuple[str, ...] = (
    "BTDoorPlus_Support",
    "BTDoorEntryPlus_Support",
)
SUPPORT_ARTIFACT_SUFFIXES: tuple[str, ...] = (".md", ".zip")


@dataclass(frozen=True, slots=True)
class SupportArtifactNames:
    """Names generated for one support report set."""

    stem: str
    report_name: str
    bundle_name: str


def build_support_artifact_names(timestamp: datetime) -> SupportArtifactNames:
    """Return deterministic names using the current project identity."""
    stamp = timestamp.strftime("%Y%m%d-%H%M%S")
    stem = f"{SUPPORT_ARTIFACT_PREFIX}_{stamp}"
    return SupportArtifactNames(
        stem=stem,
        report_name=f"{stem}.md",
        bundle_name=f"{stem}.zip",
    )


def is_managed_support_artifact(path: Path) -> bool:
    """Return whether a file belongs to the current or a legacy report set."""
    if not path.is_file() or path.suffix.lower() not in SUPPORT_ARTIFACT_SUFFIXES:
        return False
    prefixes = (SUPPORT_ARTIFACT_PREFIX, *LEGACY_SUPPORT_ARTIFACT_PREFIXES)
    return any(path.name.startswith(f"{prefix}_") for prefix in prefixes)
