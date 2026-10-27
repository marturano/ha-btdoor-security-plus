from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ["python", "tools/home_assistant_certification/ha_certification.py"]


def test_certification_assets_exist():
    for rel in (
        "docs/home-assistant-certification/HOME_ASSISTANT_CERTIFICATION_POLICY.md",
        "docs/home-assistant-certification/EXECUTION_RUNBOOK.md",
        "tools/home_assistant_certification/ha_certification.py",
    ):
        assert (ROOT / rel).is_file(), rel


def test_status_is_ready_but_not_certified():
    result = subprocess.run(TOOL + ["status"], cwd=ROOT, text=True, capture_output=True, check=True)
    data = json.loads(result.stdout)
    assert data["status"] == "READY"
    assert data["requires_live_home_assistant"] is True


def test_empty_run_cannot_validate_or_export():
    run_id = "pytest-ha-certification-incomplete"
    work = ROOT / "ha-certification-work" / run_id
    if work.exists():
        shutil.rmtree(work)
    subprocess.run(
        TOOL + ["init", "--run-id", run_id], cwd=ROOT, check=True, capture_output=True, text=True
    )
    result = subprocess.run(
        TOOL + ["validate", "--run-id", run_id, "--json"], cwd=ROOT, text=True, capture_output=True
    )
    assert result.returncode != 0
    result = subprocess.run(
        TOOL + ["export-target", "--run-id", run_id], cwd=ROOT, text=True, capture_output=True
    )
    assert result.returncode != 0
    shutil.rmtree(work)


def test_repository_does_not_claim_live_execution():
    data = json.loads(
        (ROOT / "docs/home-assistant-certification/CERTIFICATION_STATUS.json").read_text()
    )
    assert data["live_target_executed"] is False
    assert data["release_approval"] == "NOT_GRANTED"
