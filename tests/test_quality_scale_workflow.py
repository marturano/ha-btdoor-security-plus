from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_quality_scale_workflow_generates_status_and_plan():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/quality_scale/quality_scale_workflow.py"), "run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    status = json.loads(
        (ROOT / "docs/quality-scale/QUALITY_SCALE_WORKFLOW_STATUS.json").read_text()
    )
    plan = json.loads((ROOT / "docs/quality-scale/QUALITY_SCALE_REMEDIATION_PLAN.json").read_text())
    assert status["desired_tier"] == "gold"
    assert status["maximum_governed_tier"] == "gold"
    assert status["gold_policy_verified"] is True
    assert status["platinum_policy"].startswith("out_of_scope")
    assert status["release_minimum_tier"] == "gold"
    assert status["workflow_status"] == "PASS"
    assert status["current_tier"] == "gold"
    assert status["advancement_status"] == "ALLOWED"
    assert not any(item["rule_id"] == "config-flow-test-coverage" for item in plan["items"])


def test_quality_scale_workflow_is_in_official_workflow():
    workflow = (ROOT / "docs/project/WORKFLOW.md").read_text()
    assert "Quality Scale Initial Assessment" in workflow
    assert "Quality Scale Gate" in workflow
    assert "Quality Scale Remediation Verification" in workflow
