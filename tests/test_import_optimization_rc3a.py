"""Regression tests for lightweight package import in 6.0.0-rc.3a."""

from __future__ import annotations

import ast
from pathlib import Path


INTEGRATION_INIT = (
    Path(__file__).parents[1]
    / "custom_components"
    / "btdoor_security_plus"
    / "__init__.py"
)

HEAVY_SUBSYSTEMS = {
    "call_journal",
    "cloud",
    "developer",
    "device_model",
    "event_bus",
    "media",
    "runtime",
    "runtime_state",
    "sip_client",
    "support_debug",
}


def test_no_heavy_subsystem_imported_at_package_scope() -> None:
    """Heavy integration modules must be loaded lazily during entry setup."""
    tree = ast.parse(INTEGRATION_INIT.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.lstrip(".").split(".", maxsplit=1)[0])
    assert imported.isdisjoint(HEAVY_SUBSYSTEMS)


def test_certificate_probe_is_offloaded() -> None:
    """The setup-time certificate filesystem probe must not block the loop."""
    source = INTEGRATION_INIT.read_text(encoding="utf-8")
    assert "certificate_files_ready = await asyncio.to_thread(" in source
