#!/usr/bin/env python3
"""Validate the repository's GitHub Actions contract without external dependencies."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
REQUIRED_WORKFLOWS = {
    "validate.yml",
    "governance.yml",
    "github-sandbox-validation.yml",
    "release.yml",
    "ruff-remediation.yml",
}
REQUIRED_VALIDATE_MARKERS = (
    "hacs/action@",
    "home-assistant/actions/hassfest@",
    "tools/validation/github_sandbox_validate.sh check",
    "tools/check_ha_compatibility.py",
)


def main() -> int:
    errors: list[str] = []
    files = {path.name: path for path in WORKFLOW_DIR.glob("*.yml")}

    for name in sorted(REQUIRED_WORKFLOWS - files.keys()):
        errors.append(f"Missing workflow: .github/workflows/{name}")

    for name, path in sorted(files.items()):
        text = path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*\S", text):
            errors.append(f"{name}: missing workflow name")
        if not re.search(r"(?m)^on:\s*$", text):
            errors.append(f"{name}: missing explicit trigger block")
        if "workflow_dispatch:" not in text:
            errors.append(f"{name}: workflow_dispatch trigger is required")
        if not re.search(r"(?m)^permissions:\s*$", text):
            errors.append(f"{name}: explicit permissions are required")
        if "${{ runner.temp }}" in text:
            errors.append(f"{name}: runner.temp is forbidden in repository workflow env")
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if re.match(r"run:\s+(?:\./)?(?:tools|scripts)/.+\.sh(?:\s|$)", stripped):
                if not re.match(r"run:\s+bash\s+", stripped):
                    errors.append(
                        f"{name}:{line_no}: shell script must be invoked explicitly with bash"
                    )

    validate = files.get("validate.yml")
    if validate:
        text = validate.read_text(encoding="utf-8")
        for marker in REQUIRED_VALIDATE_MARKERS:
            if marker not in text:
                errors.append(f"validate.yml: missing required validation marker: {marker}")

    sandbox = files.get("github-sandbox-validation.yml")
    if sandbox:
        text = sandbox.read_text(encoding="utf-8")
        if "bash tools/validation/github_sandbox_validate.sh check" not in text:
            errors.append("github-sandbox-validation.yml: canonical validation runner is not used")
        if "git diff --exit-code" not in text:
            errors.append("github-sandbox-validation.yml: clean-tree verification is missing")

    if errors:
        print("GitHub workflow contract: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"GitHub workflow contract: PASS ({len(files)} workflows checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
