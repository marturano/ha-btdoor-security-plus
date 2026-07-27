from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_github_workflow_contract_passes() -> None:
    path = ROOT / "tools" / "validation" / "check_github_workflows.py"
    spec = importlib.util.spec_from_file_location("workflow_contract", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main() == 0
