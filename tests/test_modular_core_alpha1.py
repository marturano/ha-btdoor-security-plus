"""Regression tests for the 6.1.0-alpha.1 modular core."""

from __future__ import annotations

import ast
from pathlib import Path

from custom_components.btdoor_security_plus.core import LifecycleCleanupRegistry
from custom_components.btdoor_security_plus.models import (
    CloudSnapshot,
    DeviceDescriptor,
    RuntimeCapabilities,
    RuntimeSnapshot,
    SipSnapshot,
)

ROOT = Path(__file__).parents[1] / "custom_components" / "btdoor_security_plus"


def test_runtime_snapshot_is_immutable_and_serializable() -> None:
    snapshot = RuntimeSnapshot(
        lifecycle_state="running",
        generated_at="2026-07-20T10:00:00+00:00",
        cloud=CloudSnapshot(connected=True, authenticated=True),
        sip=SipSnapshot(registered=True, status="SIP/2.0 200 Ok"),
        capabilities=RuntimeCapabilities(media=True, support_bundle_v2=False),
    )

    assert snapshot.as_dict()["cloud"]["authenticated"] is True
    assert snapshot.as_dict()["sip"]["registered"] is True


def test_device_descriptor_has_uniform_defaults() -> None:
    descriptor = DeviceDescriptor(
        key="cloud",
        name_key="cloud_status",
        model="DS+ Suite – Cloud Status",
    )

    assert descriptor.manufacturer == "BTicino / Legrand"
    assert descriptor.suggested_area is None


def test_cleanup_registry_runs_in_reverse_order() -> None:
    calls: list[str] = []
    registry = LifecycleCleanupRegistry()
    registry.add(lambda: calls.append("first"))
    registry.add(lambda: calls.append("second"))

    assert registry.pending == 2
    assert registry.run() == ()
    assert calls == ["second", "first"]
    assert registry.pending == 0


def test_models_do_not_import_home_assistant() -> None:
    for path in (ROOT / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        assert not any(name.startswith("homeassistant") for name in imports), path
