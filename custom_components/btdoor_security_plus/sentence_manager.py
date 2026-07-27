"""Install integration-owned Assist custom sentences safely."""
from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path

from homeassistant.core import HomeAssistant

from .const import DOMAIN, INTEGRATION_VERSION

MANAGED_MARKER = "# Managed by BTDoor Security+; local edits will be preserved."


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _install(source_root: Path, config_root: Path) -> dict[str, int]:
    installed = updated = preserved = 0
    for source in source_root.glob("*/btdoor_security_plus.yaml"):
        language = source.parent.name
        destination = config_root / "custom_sentences" / language / f"{DOMAIN}.yaml"
        hash_path = destination.with_suffix(".sha256")
        destination.parent.mkdir(parents=True, exist_ok=True)
        source_bytes = source.read_bytes()
        managed = (
            f"{MANAGED_MARKER}\n# Version: {INTEGRATION_VERSION}\n".encode("utf-8")
            + source_bytes
        )
        new_hash = _digest(managed)
        if not destination.exists():
            destination.write_bytes(managed)
            hash_path.write_text(new_hash, encoding="utf-8")
            installed += 1
            continue
        previous_hash = hash_path.read_text(encoding="utf-8").strip() if hash_path.exists() else ""
        current_hash = _digest(destination.read_bytes())
        if current_hash == new_hash:
            # Already current: keep installation idempotent across restarts.
            hash_path.write_text(new_hash, encoding="utf-8")
        elif previous_hash and current_hash == previous_hash:
            destination.write_bytes(managed)
            hash_path.write_text(new_hash, encoding="utf-8")
            updated += 1
        else:
            preserved += 1
    return {"installed": installed, "updated": updated, "preserved": preserved}


async def async_install_sentences(hass: HomeAssistant) -> dict[str, int]:
    """Install/update only integration-managed sentence files."""
    source_root = Path(__file__).parent / "custom_sentences"
    config_root = Path(hass.config.path())
    return await asyncio.to_thread(_install, source_root, config_root)
