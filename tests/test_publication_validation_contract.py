"""The preflight must follow delegation without accepting missing Python gates."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "publication_preflight", ROOT / "tools/publication/check_repository_publication.py"
)
assert SPEC and SPEC.loader
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


@pytest.mark.parametrize("missing", [None, "mypy", "pytest", "ruff-check", "delegation"])
def test_publication_checks_delegated_gates(tmp_path, missing):
    workflow = ROOT / ".github/workflows/validate.yml"
    runner = ROOT / "tools/validation/github_sandbox_validate.sh"
    for source in (workflow, runner):
        target = tmp_path / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = source.read_text(encoding="utf-8")
        if missing == "delegation" and source == workflow:
            text = text.replace("bash tools/validation/github_sandbox_validate.sh check", "true")
        elif missing and source == runner:
            text = "\n".join(
                line for line in text.splitlines() if not line.startswith(f"run_logged {missing} ")
            )
        target.write_text(text, encoding="utf-8")
    if missing:
        with pytest.raises(SystemExit, match="missing"):
            PREFLIGHT.check_validation_contract(tmp_path)
    else:
        PREFLIGHT.check_validation_contract(tmp_path)
