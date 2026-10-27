#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_RULES = [
    *(f"CR-{i:03d}" for i in range(1, 6)),
    *(f"RG-{i:03d}" for i in range(1, 12)),
    *(f"WR-{i:03d}" for i in range(1, 6)),
    *(f"IR-{i:03d}" for i in range(1, 4)),
    *(f"VR-{i:03d}" for i in range(1, 4)),
    *(f"RR-{i:03d}" for i in range(1, 5)),
    "MGR-001",
]
FRAMEWORKS = [
    "Development",
    "Validation",
    "Quality",
    "Localization",
    "Documentation",
    "Governance",
    "Evidence",
    "Release",
]
DOMAINS = [
    "Runtime",
    "Documents",
    "Frameworks",
    "Registries",
    "Matrices",
    "Certificates",
    "Localization",
    "Evidence",
    "Release",
    "Handoff",
]


def check() -> list[str]:
    errors: list[str] = []
    rules_path = ROOT / "docs/governance/GOVERNANCE_RULE_REGISTRY.md"
    piaf_path = ROOT / "docs/governance/PROJECT_IMPACT_ANALYSIS_FRAMEWORK.md"
    dim_path = ROOT / "docs/governance/DOCUMENT_IMPACT_MATRIX.md"
    workflow_path = ROOT / "docs/project/WORKFLOW.md"
    for path in (rules_path, piaf_path, dim_path, workflow_path):
        if not path.exists():
            errors.append(f"Missing {path.relative_to(ROOT)}")
    if errors:
        return errors
    rules = rules_path.read_text(encoding="utf-8")
    for rule in REQUIRED_RULES:
        if rule not in rules:
            errors.append(f"Governance registry missing {rule}")
    piaf = piaf_path.read_text(encoding="utf-8")
    for domain in DOMAINS:
        if not re.search(rf"\b{re.escape(domain)}\b", piaf, re.I):
            errors.append(f"PIAF missing impact domain {domain}")
    for status in ("NOT_IMPACTED", "REVIEW_REQUIRED", "UPDATE_REQUIRED", "REVALIDATION_REQUIRED"):
        if status not in piaf:
            errors.append(f"PIAF missing status {status}")
    dim = dim_path.read_text(encoding="utf-8")
    if "Framework Impact Matrix" not in dim:
        errors.append("DIM missing Framework Impact Matrix")
    for framework in FRAMEWORKS:
        if framework not in dim:
            errors.append(f"Framework Impact Matrix missing {framework}")
    workflow = workflow_path.read_text(encoding="utf-8")
    for marker in (
        "Project Impact Analysis",
        "Framework Revalidation",
        "Automatic Handoff Synchronization",
    ):
        if marker not in workflow:
            errors.append(f"Workflow missing {marker}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors = check()
    payload = {
        "gate": "project_impact",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"[{payload['status']}] project_impact")
        for error in errors:
            print(f"  - {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
