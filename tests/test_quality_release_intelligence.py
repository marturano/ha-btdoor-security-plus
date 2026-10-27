from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_quality_intelligence_files_exist():
    for rel in (
        "docs/quality/evidence_register.json",
        "docs/quality/risk_register.json",
        "docs/quality/technical_debt_register.json",
        "docs/quality/decision_traceability.json",
        "tools/evidence/quality_intelligence.py",
        "tools/release/release_decision.py",
        "tools/traceability/build_traceability.py",
    ):
        assert (ROOT / rel).exists(), rel


def test_quality_intelligence_validation_passes():
    r = subprocess.run(
        ["python", "tools/evidence/quality_intelligence.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads((ROOT / "docs/quality/quality_release_intelligence.json").read_text())
    assert data["status"] == "PASS"
    assert data["evidence_total"] >= 10


def test_release_decision_is_explainable_and_currently_blocked():
    r = subprocess.run(
        ["python", "tools/release/release_decision.py"], cwd=ROOT, text=True, capture_output=True
    )
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads((ROOT / "docs/quality/release_decision.json").read_text())
    assert data["decision"] == "BLOCKED"
    assert data["blocking_evidence"]


def test_traceability_generation_passes():
    r = subprocess.run(
        ["python", "tools/traceability/build_traceability.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
