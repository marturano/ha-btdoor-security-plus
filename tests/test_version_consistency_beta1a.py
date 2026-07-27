"""Regression tests for integration/device firmware version consistency."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "custom_components" / "btdoor_security_plus" / "manifest.json"
CONST = ROOT / "custom_components" / "btdoor_security_plus" / "const.py"
FACTORY = ROOT / "custom_components" / "btdoor_security_plus" / "device_model" / "factory.py"


def _integration_version() -> str:
    tree = ast.parse(CONST.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "INTEGRATION_VERSION":
                    return ast.literal_eval(node.value)
    raise AssertionError("INTEGRATION_VERSION not found")


def test_manifest_and_device_version_are_identical() -> None:
    manifest_version = json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]
    assert _integration_version() == manifest_version


def test_device_factory_uses_shared_version_constant() -> None:
    source = FACTORY.read_text(encoding="utf-8")
    assert "sw_version=INTEGRATION_VERSION" in source
    assert "6.1.0-alpha.4" not in source
