from __future__ import annotations
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_toolkit_files_are_present_and_parse():
    names = {"validate.py", "deploy.py", "reload.py", "restart.py", "watch.py", "logs.py", "support_bundle.py", "_ha_toolkit.py"}
    for name in names:
        path = ROOT / "tools" / name
        assert path.is_file()
        ast.parse(path.read_text(encoding="utf-8"))

def test_manifest_current_release():
    manifest=json.loads((ROOT/"custom_components"/"btdoor_security_plus"/"manifest.json").read_text())
    assert manifest["version"] == "6.0.1"
