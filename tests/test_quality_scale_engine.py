from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_quality_scale_engine_generates_reports() -> None:
    result = subprocess.run(
        [sys.executable, "tools/quality_scale/quality_scale_engine.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(
        (ROOT / "docs/quality-scale/QUALITY_SCALE_REPORT.json").read_text(encoding="utf-8")
    )
    assert report["assessment_type"].startswith("self-assessment")
    assert set(report["summaries"]) == {"bronze", "silver", "gold", "platinum"}
    assert len(report["rules"]) == 54
    assert report["achieved_tier"] == "gold"
    assert report["target_tier"] == "gold"
    assert report["maximum_governed_tier"] == "gold"
    assert report["release_gate_required_tier"] == "gold"
    assert report["release_gate_status"] == "PASS"
    assert report["platinum_policy"].startswith("out_of_scope")
    assert (ROOT / "custom_components/btdoor_security_plus/quality_scale.yaml").exists()


def test_quality_scale_does_not_claim_official_grade() -> None:
    report = json.loads(
        (ROOT / "docs/quality-scale/QUALITY_SCALE_REPORT.json").read_text(encoding="utf-8")
    )
    assert "not an official" in report["assessment_type"]
