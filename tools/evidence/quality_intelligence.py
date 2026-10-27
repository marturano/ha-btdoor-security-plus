#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/quality/evidence_register.json"
RISKS = ROOT / "docs/quality/risk_register.json"
DEBT = ROOT / "docs/quality/technical_debt_register.json"
TRACE = ROOT / "docs/quality/decision_traceability.json"
REPORT = ROOT / "docs/quality/quality_release_intelligence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    evidence = load(EVIDENCE)["evidence"]
    risks = load(RISKS)["risks"]
    debt = load(DEBT)["items"]
    trace = load(TRACE)["links"]
    ids = [e["id"] for e in evidence]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    missing_sources = []
    inconsistent = []
    for e in evidence:
        exists = path_exists(e["source"])
        if e["status"] == "VALIDATED" and not exists:
            inconsistent.append(
                {"id": e["id"], "issue": "validated source missing", "source": e["source"]}
            )
        if e["status"] in {"MISSING", "PENDING"} and exists and e["status"] == "MISSING":
            inconsistent.append(
                {
                    "id": e["id"],
                    "issue": "source exists but status is MISSING",
                    "source": e["source"],
                }
            )
        if not exists:
            missing_sources.append(e["id"])
    evidence_set = set(ids)
    bad_risk_refs = []
    for risk in risks:
        for ev in risk.get("evidence", []):
            if ev not in evidence_set:
                bad_risk_refs.append({"risk": risk["id"], "evidence": ev})
    trace_missing = []
    for link in trace:
        for field, path in link.items():
            if field != "decision" and not path_exists(path):
                trace_missing.append({"decision": link["decision"], "field": field, "path": path})
    validated = sum(e["status"] == "VALIDATED" for e in evidence)
    blocking_open = [e["id"] for e in evidence if e.get("blocking") and e["status"] != "VALIDATED"]
    open_risks = [r for r in risks if r["status"] == "OPEN"]
    critical_high = [r["id"] for r in open_risks if r["severity"] in {"CRITICAL", "HIGH"}]
    payload = {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "evidence_total": len(evidence),
        "evidence_validated": validated,
        "evidence_coverage_percent": round(validated * 100 / max(1, len(evidence)), 1),
        "blocking_evidence_open": blocking_open,
        "open_risks": len(open_risks),
        "critical_high_risks": critical_high,
        "technical_debt_open": sum(i["status"] == "OPEN" for i in debt),
        "duplicate_evidence_ids": duplicate_ids,
        "inconsistent_evidence": inconsistent,
        "invalid_risk_references": bad_risk_refs,
        "traceability_missing_paths": trace_missing,
        "status": "PASS"
        if not (duplicate_ids or inconsistent or bad_risk_refs or trace_missing)
        else "FAIL",
    }
    REPORT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Quality intelligence: {payload['status']}")
        print(f"- Evidence coverage: {payload['evidence_coverage_percent']}%")
        print(f"- Blocking evidence open: {len(blocking_open)}")
        print(f"- Critical/high risks: {len(critical_high)}")
        print(f"- Open technical debt: {payload['technical_debt_open']}")
    return 1 if args.check and payload["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
