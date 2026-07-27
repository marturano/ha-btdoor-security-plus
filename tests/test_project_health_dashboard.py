from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_project_health_source_and_rendered_dashboard_exist() -> None:
    source = ROOT / "docs/project/project_health.json"
    rendered = ROOT / "docs/project/PROJECT_HEALTH_DASHBOARD.md"
    generator = ROOT / "tools/update_project_health.py"
    assert source.is_file()
    assert rendered.is_file()
    assert generator.is_file()


def test_project_health_weights_total_100_and_evidence_exists() -> None:
    data = json.loads((ROOT / "docs/project/project_health.json").read_text(encoding="utf-8"))
    assert sum(item["weight"] for item in data["domains"]) == 100
    allowed = {"PASS", "PASS WITH CONDITIONS", "BLOCKED", "NOT APPLICABLE", "NOT STARTED"}
    for item in data["domains"]:
        assert 0 <= item["score"] <= 100
        assert item["status"] in allowed
        assert item["evidence"]
        for evidence in item["evidence"]:
            assert (ROOT / evidence).exists(), evidence


def test_workflow_contains_formal_gates_and_dashboard_update() -> None:
    workflow = (ROOT / "docs/project/WORKFLOW.md").read_text(encoding="utf-8")
    for required in (
        "Definition of Ready Gate",
        "Architecture Gate",
        "Quality Gate",
        "Security Gate",
        "Performance Gate",
        "Documentation Gate",
        "Validation Gate",
        "Release Readiness Gate",
        "Publication Gate",
        "Final Release Gate",
        "Project Health Dashboard Update",
    ):
        assert required in workflow
