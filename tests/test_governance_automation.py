from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_governance_framework_files_exist() -> None:
    for rel in (
        "tools/governance/run_governance.py",
        "tools/governance/check_governance.py",
        "tools/handoff/check_handoff.py",
        "tools/release/check_release_readiness.py",
        "tools/health/calculate_health.py",
        "docs/project/GOVERNANCE_AUTOMATION.md",
        ".github/workflows/governance.yml",
    ):
        assert (ROOT / rel).exists(), rel


def test_health_calculator_generates_machine_readable_output() -> None:
    result = subprocess.run(
        ["python", "tools/health/calculate_health.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(
        (ROOT / "docs/project/project_health_calculated.json").read_text(encoding="utf-8")
    )
    assert 0 <= data["health_score"] <= 100
    assert 0 <= data["compliance_score"] <= 100
    assert not data["evidence_errors"]


def test_governance_and_handoff_checks_pass() -> None:
    for script in (
        "tools/governance/check_governance.py",
        "tools/handoff/check_handoff.py",
        "tools/release/check_release_readiness.py",
    ):
        result = subprocess.run(["python", script], cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, result.stdout + result.stderr
