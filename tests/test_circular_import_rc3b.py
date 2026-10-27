"""Regression tests for the 6.0.0-rc.3b circular import hotfix."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "btdoor_security_plus"


def test_device_model_package_does_not_eagerly_import_manager() -> None:
    source = (PACKAGE / "device_model" / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level_imports = [
        node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    assert not any(
        isinstance(node, ast.ImportFrom) and node.module == "manager" for node in top_level_imports
    )


def test_device_model_manager_keeps_visibility_dependency_out_of_package_init() -> None:
    package_source = (PACKAGE / "device_model" / "__init__.py").read_text(encoding="utf-8")
    manager_source = (PACKAGE / "device_model" / "manager.py").read_text(encoding="utf-8")
    assert "from .manager import async_register_devices" in package_source
    assert "from ..visibility import visibility_for_entry" in manager_source
    assert package_source.index(
        "from .manager import async_register_devices"
    ) > package_source.index("async def async_register_devices")


def test_visibility_imports_factory_without_triggering_manager() -> None:
    source = (PACKAGE / "visibility" / "manager.py").read_text(encoding="utf-8")
    assert "from ..device_model.factory import DeviceKind" in source
