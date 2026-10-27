from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/audit/production_audit.py"

spec = importlib.util.spec_from_file_location("production_audit", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_production_audit_passes_repository():
    payload = module.audit()
    assert payload["status"] == "PASS"
    assert all(payload["checks"].values())


def test_production_audit_never_grants_publication():
    payload = module.audit()
    assert payload["release_context"]["publication_approval"] == "NOT_GRANTED"


def test_required_documentation_exists():
    for path in [
        "docs/production-audit/README.md",
        "docs/production-audit/PRODUCTION_AUDIT_POLICY.md",
        "docs/adr/ADR-0063-repository-production-audit.md",
        "handoff/36_REPOSITORY_PRODUCTION_AUDIT_STATUS.md",
    ]:
        assert (ROOT / path).is_file(), path


@pytest.mark.parametrize("unexpected_empty_directory", [False, True])
def test_hygiene_excludes_git_metadata_but_checks_project_directories(
    tmp_path, unexpected_empty_directory
):
    tools = tmp_path / "tools"
    tools.mkdir()
    shutil.copyfile(ROOT / "tools/check_orphans.py", tools / "check_orphans.py")
    for name in (
        "docs/project/REPOSITORY_INVENTORY.md",
        "docs/validation/VALIDATION_MAINTENANCE_POLICY.md",
        "docs/validation/VALIDATION_REGISTER.md",
        "docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")
    (tmp_path / ".git/refs/tags").mkdir(parents=True)
    if unexpected_empty_directory:
        (tmp_path / "unexpected-empty").mkdir()
    result = subprocess.run(
        [sys.executable, str(tools / "check_orphans.py")], capture_output=True, text=True
    )
    if unexpected_empty_directory:
        assert result.returncode == 1
        assert "empty directory: unexpected-empty" in result.stdout
    else:
        assert result.returncode == 0, result.stdout + result.stderr
    assert ".git" not in result.stdout
