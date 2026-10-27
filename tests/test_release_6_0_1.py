"""Stable maintenance release regression checks for 6.0.1."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"


def test_release_version_is_consistent() -> None:
    manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))
    module = ast.parse((COMPONENT / "const.py").read_text(encoding="utf-8"))
    version = next(
        node.value.value
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "INTEGRATION_VERSION"
            for target in node.targets
        )
        and isinstance(node.value, ast.Constant)
    )
    assert manifest["version"] == "1.1.0-rc.15"
    assert version == manifest["version"]
