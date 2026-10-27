#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/project/project_health.json"
OUT = ROOT / "docs/project/project_health_calculated.json"

STATUS_FACTOR = {
    "PASS": 1.0,
    "PASS WITH CONDITIONS": 0.85,
    "NOT STARTED": 0.45,
    "BLOCKED": 0.2,
    "FAIL": 0.0,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    evidence_errors = []
    rows = []
    for d in data["domains"]:
        existing = [p for p in d["evidence"] if (ROOT / p).exists()]
        missing = [p for p in d["evidence"] if not (ROOT / p).exists()]
        if missing:
            evidence_errors.extend(f"{d['id']}: {p}" for p in missing)
        coverage = round(100 * len(existing) / max(1, len(d["evidence"])))
        governed_score = int(d["score"])
        calculated = round(min(governed_score, coverage) * STATUS_FACTOR.get(d["status"], 0.5))
        rows.append(
            {
                **d,
                "evidence_coverage": coverage,
                "calculated_score": calculated,
                "missing_evidence": missing,
            }
        )
    total = sum(r["weight"] for r in rows)
    health = round(sum(r["calculated_score"] * r["weight"] for r in rows) / total)
    compliance = round(
        sum(
            (100 if not r["missing_evidence"] else r["evidence_coverage"]) * r["weight"]
            for r in rows
        )
        / total
    )
    payload = {
        "schema_version": 1,
        "project": data["project"],
        "package": data["package"],
        "target": data["target"],
        "health_score": health,
        "compliance_score": compliance,
        "domains": rows,
        "evidence_errors": evidence_errors,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Health {health}/100 | Compliance {compliance}/100 | missing evidence {len(evidence_errors)}"
    )
    return 1 if args.check and evidence_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
