from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gold_is_the_fixed_project_quality_scale_policy() -> None:
    config = json.loads((ROOT / "docs/quality-scale/quality_scale_workflow.json").read_text())
    assert config["release_minimum_tier"] == "gold"
    assert config["desired_tier"] == "gold"
    assert config["maximum_governed_tier"] == "gold"
    assert config["platinum_policy"].startswith("out_of_scope")


def test_gold_policy_is_enforced_by_strict_workflow_check() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/quality_scale/quality_scale_workflow.py"), "check"],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr or result.stdout
    status = json.loads((ROOT / "docs/quality-scale/QUALITY_SCALE_WORKFLOW_STATUS.json").read_text())
    assert status["current_tier"] == "gold"
    assert status["gold_policy_verified"] is True
    assert status["advancement_status"] == "ALLOWED"
