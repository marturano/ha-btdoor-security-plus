"""Stable release regression checks for the current 6.0.x release."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _integration_version() -> str:
    tree = ast.parse((PKG / "const.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "INTEGRATION_VERSION":
                    assert isinstance(node.value, ast.Constant)
                    return str(node.value.value)
    raise AssertionError("INTEGRATION_VERSION not found")


def test_manifest_and_device_software_version_match() -> None:
    manifest = json.loads((PKG / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "1.1.0-rc.15"
    assert _integration_version() == manifest["version"]


def test_registry_identifiers_remain_stable() -> None:
    source = (PKG / "device_model" / "factory.py").read_text(encoding="utf-8")
    assert 'f"{kind.value}_{_root_key(entry)}"' in source
    assert 'f"sip_client_{id_device}"' in source
    assert 'info["via_device"] = root' in source


def test_user_device_names_are_never_overwritten() -> None:
    source = (PKG / "device_model" / "manager.py").read_text(encoding="utf-8")
    assert "device.name_by_user is None" in source
