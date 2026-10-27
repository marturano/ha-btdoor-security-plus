#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "handoff"
REQUIRED_CURRENT = [
    "03_PROJECT_STATE.md",
    "14_BUILD_INFORMATION.md",
    "28_IMMEDIATE_RESUME_POINT.md",
]


def package_identity() -> str:
    text = (HANDOFF / "HANDOFF_INDEX.md").read_text(encoding="utf-8")
    match = re.search(r"\*\*Current package:\*\* `([^`]+)`", text)
    return match.group(1) if match else ""


def validate() -> list[str]:
    errors: list[str] = []
    index = HANDOFF / "HANDOFF_INDEX.md"
    if not index.exists():
        return ["Missing handoff/HANDOFF_INDEX.md"]
    identity = package_identity()
    if not identity:
        errors.append("HANDOFF_INDEX missing current package identity")
    index_text = index.read_text(encoding="utf-8")
    for name in REQUIRED_CURRENT:
        path = HANDOFF / name
        if not path.exists():
            errors.append(f"Missing handoff/{name}")
            continue
        if name not in index_text:
            errors.append(f"HANDOFF_INDEX omits {name}")
        text = path.read_text(encoding="utf-8")
        if identity and identity not in text:
            errors.append(f"handoff/{name} does not reference current package {identity}")
    numbered = sorted(HANDOFF.glob("[0-9][0-9]_*.md"))
    if not numbered:
        errors.append("No numbered iteration handoff found")
    else:
        latest = numbered[-1]
        if latest.name not in index_text:
            errors.append(f"HANDOFF_INDEX omits latest numbered handoff {latest.name}")
        if identity and identity not in latest.read_text(encoding="utf-8"):
            errors.append(
                f"Latest numbered handoff {latest.name} does not reference current package"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors = validate()
    payload = {
        "gate": "handoff_synchronization",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"[{payload['status']}] handoff_synchronization")
        for error in errors:
            print(f"  - {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
