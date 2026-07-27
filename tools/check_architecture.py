#!/usr/bin/env python3
"""Validate the dependency boundaries of the BTDoor runtime."""

from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1] / "custom_components" / "btdoor_security_plus"
RULES = {
    "models": ("homeassistant", "custom_components.btdoor_security_plus.managers"),
    "core": (
        "custom_components.btdoor_security_plus.sensor",
        "custom_components.btdoor_security_plus.binary_sensor",
        "custom_components.btdoor_security_plus.switch",
        "custom_components.btdoor_security_plus.button",
        "custom_components.btdoor_security_plus.event",
    ),
}


def imports_for(path: Path) -> tuple[str, ...]:
    """Return imports found in one Python source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.append(node.module)
    return tuple(values)


def main() -> int:
    """Validate architecture rules and return a shell exit status."""
    violations: list[str] = []
    for layer, forbidden_prefixes in RULES.items():
        directory = ROOT / layer
        for path in directory.rglob("*.py"):
            for imported in imports_for(path):
                if imported.startswith(forbidden_prefixes):
                    violations.append(f"{path.relative_to(ROOT)} imports {imported}")
    if violations:
        print("Architecture violations:")
        print("\n".join(f"- {item}" for item in violations))
        return 1
    print("Architecture dependency rules: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
