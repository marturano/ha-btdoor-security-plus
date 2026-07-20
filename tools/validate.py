#!/usr/bin/env python3
"""Fast validation suitable for pre-deploy use."""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path
from _ha_toolkit import ROOT, SOURCE_COMPONENT

errors: list[str] = []
for path in ROOT.rglob("*.py"):
    if any(part in {".git", ".pytest_cache", "__pycache__"} for part in path.parts):
        continue
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as err:
        errors.append(f"Python: {path.relative_to(ROOT)}: {err}")
for path in ROOT.rglob("*.json"):
    if any(part in {".git", ".pytest_cache", "__pycache__"} for part in path.parts):
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as err:
        errors.append(f"JSON: {path.relative_to(ROOT)}: {err}")
manifest = json.loads((SOURCE_COMPONENT / "manifest.json").read_text(encoding="utf-8"))
if manifest.get("domain") != "btdoor_security_plus":
    errors.append("manifest.json has an unexpected domain")
if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print(f"Validation passed: {manifest['domain']} {manifest['version']}")
