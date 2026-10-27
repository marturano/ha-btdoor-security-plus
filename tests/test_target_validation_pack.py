from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/target_validation/target_validation.py"


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_target_validation_assets_exist() -> None:
    for relative in (
        "docs/target-validation/TARGET_VALIDATION_POLICY.md",
        "docs/target-validation/FIELD_EXECUTION_CHECKLIST.md",
        "docs/target-validation/EVIDENCE_SANITIZATION_GUIDE.md",
        "docs/target-validation/target_validation_plan.json",
        "tools/target_validation/target_validation.py",
    ):
        assert (ROOT / relative).is_file()


def test_init_generates_checklist_and_status(tmp_path: Path) -> None:
    run_id = "pytest-field-kit"
    work = ROOT / "target-validation-work" / run_id
    if work.exists():
        import shutil

        shutil.rmtree(work)
    try:
        result = run_tool("init", "--run-id", run_id)
        assert result.returncode == 0, result.stderr
        assert (work / "CHECKLIST.md").is_file()
        data = json.loads((work / "result.json").read_text(encoding="utf-8"))
        assert data["sections"]["runtime"]["evidence_id"] == "EV-PERF-002"
        status = run_tool("status", "--run-id", run_id)
        assert status.returncode == 0
        payload = json.loads(status.stdout)
        assert payload["required_checks"] == 19
        assert payload["ready_for_import"] is False
    finally:
        if work.exists():
            import shutil

            shutil.rmtree(work)


def test_import_rejects_incomplete_run() -> None:
    run_id = "pytest-incomplete-import"
    work = ROOT / "target-validation-work" / run_id
    if work.exists():
        import shutil

        shutil.rmtree(work)
    try:
        assert run_tool("init", "--run-id", run_id).returncode == 0
        result = run_tool("import", "--run-id", run_id)
        assert result.returncode != 0
        assert "Run rejected" in result.stderr
    finally:
        if work.exists():
            import shutil

            shutil.rmtree(work)


def test_validate_rejects_path_traversal() -> None:
    run_id = "pytest-unsafe-evidence"
    work = ROOT / "target-validation-work" / run_id
    if work.exists():
        import shutil

        shutil.rmtree(work)
    try:
        assert run_tool("init", "--run-id", run_id).returncode == 0
        result_path = work / "result.json"
        data = json.loads(result_path.read_text(encoding="utf-8"))
        data["environment"].update(
            {
                "home_assistant_version": "2026.7.2",
                "installation_type": "Home Assistant OS",
                "host": "ha-target",
            }
        )
        for section in data["sections"].values():
            section["status"] = "VALIDATED"
            for check in section["checks"].values():
                check["status"] = "VALIDATED"
                check["evidence"] = ["../../secret.txt"]
        data["operator_attestation"] = {
            "name": "Operator",
            "date": "2026-07-23",
            "statement": "I attest the retained evidence is accurate and sanitized.",
        }
        result_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        result = run_tool("validate", "--run-id", run_id)
        assert result.returncode != 0
        assert "unsafe evidence path" in result.stdout
    finally:
        if work.exists():
            import shutil

            shutil.rmtree(work)


def _complete_run(run_id: str, version: str) -> Path:
    work = ROOT / "target-validation-work" / run_id
    if work.exists():
        import shutil

        shutil.rmtree(work)
    assert run_tool("init", "--run-id", run_id).returncode == 0
    evidence = work / "evidence" / "proof.txt"
    evidence.write_text("sanitized evidence\n", encoding="utf-8")
    result_path = work / "result.json"
    data = json.loads(result_path.read_text(encoding="utf-8"))
    data["environment"].update(
        {
            "home_assistant_version": version,
            "installation_type": "Home Assistant OS",
            "host": "ha-target",
        }
    )
    for section in data["sections"].values():
        section["status"] = "VALIDATED"
        for check in section["checks"].values():
            check["status"] = "VALIDATED"
            check["evidence"] = ["evidence/proof.txt"]
    data["operator_attestation"] = {
        "name": "Operator",
        "date": "2026-07-23",
        "statement": "I attest the retained evidence is accurate and sanitized.",
    }
    result_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return work


def test_validate_accepts_supported_2026_series_target() -> None:
    run_id = "pytest-supported-2026-series"
    work = _complete_run(run_id, "2026.4.9")
    try:
        result = run_tool("validate", "--run-id", run_id)
        assert result.returncode == 0, result.stdout + result.stderr
        status = run_tool("status", "--run-id", run_id)
        payload = json.loads(status.stdout)
        assert payload["target_series"] == "2026.x"
        assert payload["reference_target"] is False
    finally:
        import shutil

        shutil.rmtree(work)


def test_status_marks_2026_7_as_reference_target() -> None:
    run_id = "pytest-reference-2026-7"
    work = _complete_run(run_id, "2026.7.2")
    try:
        status = run_tool("status", "--run-id", run_id)
        payload = json.loads(status.stdout)
        assert payload["ready_for_import"] is True
        assert payload["reference_target"] is True
    finally:
        import shutil

        shutil.rmtree(work)


def test_validate_rejects_non_2026_target() -> None:
    run_id = "pytest-unsupported-series"
    work = _complete_run(run_id, "2025.12.4")
    try:
        result = run_tool("validate", "--run-id", run_id)
        assert result.returncode != 0
        assert "supported 2026.x series" in result.stdout
    finally:
        import shutil

        shutil.rmtree(work)


def test_run_id_rejects_path_traversal_and_separators() -> None:
    for run_id in ("../escape", "nested/run", "nested\\run", "..", "bad id"):
        result = run_tool("init", "--run-id", run_id)
        assert result.returncode != 0
        assert "Invalid run id" in result.stderr


def test_validate_rejects_result_run_id_mismatch() -> None:
    run_id = "pytest-run-id-mismatch"
    work = ROOT / "target-validation-work" / run_id
    if work.exists():
        import shutil

        shutil.rmtree(work)
    try:
        assert run_tool("init", "--run-id", run_id).returncode == 0
        result_path = work / "result.json"
        data = json.loads(result_path.read_text(encoding="utf-8"))
        data["run_id"] = "different-run"
        result_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        result = run_tool("validate", "--run-id", run_id)
        assert result.returncode != 0
        assert "run_id does not match the run directory" in result.stdout
    finally:
        if work.exists():
            import shutil

            shutil.rmtree(work)
