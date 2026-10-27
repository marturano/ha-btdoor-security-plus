#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/quality/evidence_register.json"
RISKS = ROOT / "docs/quality/risk_register.json"
OUT_JSON = ROOT / "docs/quality/release_decision.json"
OUT_MD = ROOT / "docs/quality/RELEASE_DECISION_REPORT.md"
QUALITY_SCALE = ROOT / "docs/quality-scale/QUALITY_SCALE_REPORT.json"
LOCALIZATION = ROOT / "docs/i18n/LOCALIZATION_REPORT.json"
DOC_AUDIT = ROOT / "docs/governance/documentation_consolidation_audit.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    evidence = load(EVIDENCE)["evidence"]
    risks = load(RISKS)["risks"]
    gates = {}
    for e in evidence:
        gates.setdefault(e["gate"], []).append(e)
    gate_results = []
    for gate, items in gates.items():
        open_items = [e["id"] for e in items if e.get("blocking") and e["status"] != "VALIDATED"]
        gate_results.append(
            {
                "gate": gate,
                "status": "PASS" if not open_items else "BLOCKED",
                "blocking_evidence": open_items,
            }
        )
    open_severe = [
        r["id"] for r in risks if r["status"] == "OPEN" and r["severity"] in {"CRITICAL", "HIGH"}
    ]
    blockers = [e["id"] for e in evidence if e.get("blocking") and e["status"] != "VALIDATED"]
    quality_scale = (
        load(QUALITY_SCALE)
        if QUALITY_SCALE.exists()
        else {"release_gate_status": "BLOCKED", "achieved_tier": "unknown"}
    )
    if (
        quality_scale.get("release_gate_status") != "PASS"
        or str(quality_scale.get("achieved_tier", "")).lower() != "gold"
    ):
        blockers.append("EV-HAQS-001")
    localization = load(LOCALIZATION) if LOCALIZATION.exists() else {"status": "FAIL"}
    documentation = load(DOC_AUDIT) if DOC_AUDIT.exists() else {"status": "FAIL"}
    if localization.get("status") != "PASS":
        blockers.append("EV-LOCALIZATION-001")
    if documentation.get("status") != "PASS":
        blockers.append("EV-DOCUMENTATION-001")
    decision = "APPROVED" if not blockers and not open_severe else "BLOCKED"
    payload = {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "target": "1.1.0 Final",
        "decision": decision,
        "gate_results": gate_results,
        "blocking_evidence": blockers,
        "critical_high_open_risks": open_severe,
        "home_assistant_quality_scale": {
            "achieved_tier": quality_scale.get("achieved_tier"),
            "gate_status": quality_scale.get("release_gate_status"),
        },
        "localization_completeness": localization.get("status"),
        "documentation_completeness": documentation.get("status"),
        "governance_rules": ["RG-001", "RG-002", "RG-003", "RG-004"],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Release Decision Report",
        "",
        f"**Generated:** {payload['generated']}",
        f"**Target:** {payload['target']}",
        f"**Decision:** **{decision}**",
        "",
        "## Gate decisions",
        "",
        "| Gate | Status | Blocking evidence |",
        "|---|---|---|",
    ]
    for g in gate_results:
        lines.append(
            f"| {g['gate']} | {g['status']} | {', '.join(g['blocking_evidence']) or 'None'} |"
        )
    lines += ["", "## Blocking evidence", ""] + ([f"- `{x}`" for x in blockers] or ["- None"])
    lines += ["", "## Critical and high open risks", ""] + (
        [f"- `{x}`" for x in open_severe] or ["- None"]
    )
    lines += [
        "",
        "## Decision rule",
        "",
        "The Final release is approved only when every blocking evidence item is validated, no open CRITICAL or HIGH risk remains without an explicitly approved exception, Quality Scale is GOLD, and RG-001 through RG-004 pass for the exact package.",
        "",
        "## Approval semantics",
        "",
        "Release Readiness `PASS` confirms package-level readiness checks only; Final approval remains `BLOCKED` until the Release Decision Engine returns `APPROVED`.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Release decision: {decision}")
    return 1 if args.check and decision != "APPROVED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
