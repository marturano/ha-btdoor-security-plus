#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "governance"))
from common import CheckResult, exists, read

REQUIRED = [
    "handoff/HANDOFF_INDEX.md",
    "handoff/16_RECOVERY_PROMPT.md",
    "handoff/24_OFFICIAL_WORKFLOW.md",
    "handoff/28_IMMEDIATE_RESUME_POINT.md",
    "handoff/29_PROJECT_HEALTH_DASHBOARD.md",
]
MARKERS = {
    "handoff/16_RECOVERY_PROMPT.md": ("workflow", "roadmap", "resume", "source of truth"),
    "handoff/28_IMMEDIATE_RESUME_POINT.md": ("next", "validation", "health"),
    "handoff/24_OFFICIAL_WORKFLOW.md": ("release readiness", "validation maintenance"),
}


def run() -> CheckResult:
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not exists(rel):
            errors.append(f"Missing {rel}")
    for rel, markers in MARKERS.items():
        text = read(rel).lower()
        for marker in markers:
            if marker not in text:
                warnings.append(f"{rel} does not contain marker: {marker}")
    return CheckResult("handoff", "PASS" if not errors else "FAIL", errors, warnings, REQUIRED)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = run()
    print(
        json.dumps(r.to_dict(), indent=2)
        if args.json
        else f"[{r.status}] handoff\n"
        + "\n".join(f"  ERROR: {x}" for x in r.errors)
        + ("\n" if r.errors else "")
        + "\n".join(f"  WARN: {x}" for x in r.warnings)
    )
    return 0 if r.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
