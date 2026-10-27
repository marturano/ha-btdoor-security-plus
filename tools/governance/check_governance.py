#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re

from common import CheckResult, exists, read

REQUIRED = {
    "constitution": "docs/project/PROJECT_CONSTITUTION.md",
    "workflow": "docs/project/WORKFLOW.md",
    "workflow_gates": "docs/project/WORKFLOW_GATES.md",
    "dor": "docs/project/DEFINITION_OF_READY.md",
    "dod": "docs/project/DEFINITION_OF_DONE.md",
    "quality_policy": "docs/quality/QUALITY_POLICY.md",
    "security_policy": "docs/security/SECURITY_POLICY.md",
    "benchmark_policy": "docs/benchmarks/BENCHMARK_POLICY.md",
    "validation_policy": "docs/validation/VALIDATION_MAINTENANCE_POLICY.md",
    "repository_policy": "docs/repository/REPOSITORY_POLICY.md",
}
MANDATORY_GATES = (
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
)
MANDATORY_STEPS = (
    "Project Scope Review",
    "Architecture Review",
    "Static Analysis",
    "Unit Tests",
    "Integration Tests",
    "Regression Tests",
    "Accessibility Review",
    "Compatibility Verification",
    "Validation Maintenance",
    "Publication Readiness",
    "Lessons Learned",
)


def run() -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    evidence = list(REQUIRED.values())
    for name, rel in REQUIRED.items():
        if not exists(rel):
            errors.append(f"Missing governed document: {name} ({rel})")
    workflow = read(REQUIRED["workflow"])
    gates = read(REQUIRED["workflow_gates"])
    for marker in MANDATORY_STEPS:
        if marker.lower() not in workflow.lower():
            errors.append(f"Workflow omits mandatory step: {marker}")
    for marker in MANDATORY_GATES:
        if marker.lower() not in (workflow + "\n" + gates).lower():
            errors.append(f"Governance omits mandatory gate: {marker}")
    if not re.search(r"Validation Maintenance.{0,80}Release Readiness", workflow, re.I | re.S):
        warnings.append(
            "Could not prove Validation Maintenance precedes Release Readiness from workflow text."
        )
    return CheckResult("governance", "PASS" if not errors else "FAIL", errors, warnings, evidence)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"[{result.status}] {result.check}")
        for item in result.errors:
            print(f"  ERROR: {item}")
        for item in result.warnings:
            print(f"  WARN: {item}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
