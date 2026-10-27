#!/usr/bin/env python3
"""Render the governed Project Health Dashboard from project_health.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/project/project_health.json"
OUTPUT = ROOT / "docs/project/PROJECT_HEALTH_DASHBOARD.md"
CALCULATED = ROOT / "docs/project/project_health_calculated.json"


def bar(score: int) -> str:
    filled = max(0, min(10, round(score / 10)))
    return "█" * filled + "░" * (10 - filled)


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    calculated = json.loads(CALCULATED.read_text(encoding="utf-8")) if CALCULATED.exists() else None
    domains = data["domains"]
    total_weight = sum(item["weight"] for item in domains)
    overall = round(sum(item["score"] * item["weight"] for item in domains) / total_weight)
    blockers = [item for item in domains if item["status"] == "BLOCKED"]
    not_started = [item for item in domains if item["status"] == "NOT STARTED"]
    label = "HEALTHY" if overall >= 90 else "WATCH" if overall >= 70 else "AT RISK"

    lines = [
        "# Project Health Dashboard",
        "",
        "**Status:** Governed, generated project artifact  ",
        f"**Package:** `{data['package']}`  ",
        f"**Target:** `{data['target']}`  ",
        f"**Last update:** `{data['updated']}`  ",
        "**Source:** `docs/project/project_health.json`  ",
        "**Regenerate:** `python tools/health/calculate_health.py && python tools/update_project_health.py`",
        "",
        "## Executive health",
        "",
        f"- **Governed assessment score:** **{overall}/100 — {label}**",
        f"- **Automated evidence-adjusted health:** **{calculated['health_score']}/100**"
        if calculated
        else "- **Automated evidence-adjusted health:** not generated",
        f"- **Governance compliance score:** **{calculated['compliance_score']}/100**"
        if calculated
        else "- **Governance compliance score:** not generated",
        f"- **Blocking domains:** **{len(blockers)}**",
        f"- **Domains not started:** **{len(not_started)}**",
        "- **Interpretation:** package integrity is strong, but Final Release readiness remains constrained by measured benchmarks, security/runtime evidence, compatibility execution and HACS/GitHub publication validation.",
        "- **Approval semantics:** Release Readiness `PASS` confirms package-level readiness checks only; Final approval remains `BLOCKED` until the Release Decision Engine returns `APPROVED`.",
        "",
        "## Domain scorecard",
        "",
        "| Domain | Weight | Score | Status | Health | Next action |",
        "|---|---:|---:|---|---|---|",
    ]
    for item in domains:
        lines.append(
            f"| {item['name']} | {item['weight']}% | {item['score']} | {item['status']} | `{bar(item['score'])}` | {item['next_action']} |"
        )
    lines += ["", "## Blocking path to 1.1.0 Final", ""]
    ordered = blockers + not_started
    if not ordered:
        lines.append("No blocking or not-started domain is recorded.")
    else:
        for item in ordered:
            lines.append(f"- **{item['name']} — {item['status']}:** {item['next_action']}")
    lines += ["", "## Evidence map", ""]
    for item in domains:
        lines.append(f"### {item['name']}")
        lines.append("")
        for evidence in item["evidence"]:
            lines.append(f"- `{evidence}`")
        lines.append("")
    lines += [
        "## Maintenance contract",
        "",
        "1. Update the underlying review, register or report first.",
        "2. Run `python tools/health/calculate_health.py`; do not hand-edit the calculated output.",
        "3. Update `project_health.json` only from repository evidence; never from chat claims.",
        "4. Regenerate this file after Validation Maintenance and Update, before Release Readiness, after gate changes and at release closure.",
        "5. A dashboard score never overrides a blocked gate or missing mandatory evidence.",
        "6. Record score-model changes in an ADR and in the Engineering Notebook.",
        "",
    ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rendered {OUTPUT.relative_to(ROOT)} with score {overall}/100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
