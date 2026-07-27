#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "docs/quality-scale/quality_scale_workflow.json"
REPORT = ROOT / "docs/quality-scale/QUALITY_SCALE_REPORT.json"
PLAN_JSON = ROOT / "docs/quality-scale/QUALITY_SCALE_REMEDIATION_PLAN.json"
PLAN_MD = ROOT / "docs/quality-scale/QUALITY_SCALE_REMEDIATION_PLAN.md"
STATUS_JSON = ROOT / "docs/quality-scale/QUALITY_SCALE_WORKFLOW_STATUS.json"
LEVELS = ("bronze", "silver", "gold", "platinum")

REMEDIATION = {
    "config-flow-test-coverage": (
        "test-coverage",
        "manual",
        "Add Home Assistant config-flow tests covering success, invalid input, connection failure, duplicate prevention and reauthentication.",
    ),
    "log-when-unavailable": (
        "functional-code",
        "manual",
        "Implement and test one-time unavailable and recovered transition logging without log spam.",
    ),
    "parallel-updates": (
        "architecture",
        "manual",
        "Review every polling platform and declare a justified PARALLEL_UPDATES value where applicable.",
    ),
    "test-coverage": (
        "test-coverage",
        "manual",
        "Measure integration coverage and close all gaps until the official threshold is demonstrated.",
    ),
    "stale-devices": (
        "functional-code",
        "manual",
        "Implement and test removal or repair handling for stale devices when the upstream inventory changes.",
    ),
    "async-dependency": (
        "dependency-behaviour",
        "manual",
        "Prove that all runtime dependencies are fully asynchronous or isolate blocking work with Home Assistant executors.",
    ),
    "inject-websession": (
        "architecture",
        "manual",
        "Use Home Assistant's shared aiohttp session throughout the integration and dependencies.",
    ),
    "strict-typing": (
        "typing",
        "manual",
        "Enable strict type checking for the integration and resolve all reported issues.",
    ),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_engine() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools/quality_scale/quality_scale_engine.py")],
        cwd=ROOT,
        check=True,
    )


def tier_index(name: str) -> int:
    return LEVELS.index(name) if name in LEVELS else -1


def create_plan(report: dict, config: dict) -> dict:
    desired = config["desired_tier"]
    required = config["release_minimum_tier"]
    maximum = config.get("maximum_governed_tier", desired)
    if desired != "gold" or required != "gold" or maximum != "gold":
        raise ValueError("Project Quality Scale policy requires desired, minimum and maximum governed tier to remain GOLD")
    max_index = tier_index(desired)
    items = []
    for rule in report["rules"]:
        if tier_index(rule["tier"]) <= max_index and rule["status"] == "todo":
            category, mode, action = REMEDIATION.get(
                rule["id"],
                (
                    "assessment",
                    "manual",
                    f"Review and implement the official requirement for {rule['id']}.",
                ),
            )
            items.append(
                {
                    "rule_id": rule["id"],
                    "tier": rule["tier"],
                    "category": category,
                    "execution_mode": mode,
                    "status": "OPEN",
                    "action": action,
                    "blocking_release_minimum": tier_index(rule["tier"])
                    <= tier_index(config["release_minimum_tier"]),
                    "evidence_required": True,
                }
            )
    return {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "current_tier": report["achieved_tier"],
        "release_minimum_tier": required,
        "maximum_governed_tier": maximum,
        "platinum_policy": config.get("platinum_policy", "out_of_scope"),
        "desired_tier": desired,
        "release_gate_status": report["release_gate_status"],
        "desired_tier_status": "ACHIEVED"
        if tier_index(report["achieved_tier"]) >= max_index
        else "IN_PROGRESS",
        "open_items": len(items),
        "automatic_items": sum(i["execution_mode"] == "automatic" for i in items),
        "manual_items": sum(i["execution_mode"] == "manual" for i in items),
        "items": items,
    }


def write_plan(plan: dict) -> None:
    PLAN_JSON.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Home Assistant Quality Scale Remediation Plan",
        "",
        f"**Generated:** {plan['generated']}",
        f"**Current tier:** {plan['current_tier'].upper()}",
        f"**Release minimum:** {plan['release_minimum_tier'].upper()}",
        f"**Desired tier:** {plan['desired_tier'].upper()}",
        f"**Maximum governed tier:** {plan['maximum_governed_tier'].upper()}",
        f"**Platinum policy:** {plan['platinum_policy']}",
        f"**Release gate:** {plan['release_gate_status']}",
        f"**Desired-tier progress:** {plan['desired_tier_status']}",
        "",
        "## Open remediation items",
        "",
        "| Tier | Rule | Mode | Release blocker | Required action |",
        "|---|---|---|---|---|",
    ]
    for item in plan["items"]:
        blocker = "YES" if item["blocking_release_minimum"] else "NO"
        lines.append(
            f"| {item['tier'].title()} | `{item['rule_id']}` | "
            f"{item['execution_mode']} | {blocker} | {item['action']} |"
        )
    if not plan["items"]:
        lines.append("| - | - | - | - | No remediation is required. |")
    lines += [
        "",
        "## Automation boundary",
        "",
        "Only deterministic documentation, metadata and validation-scaffolding changes may be applied automatically. Functional code, runtime evidence, coverage claims, architecture changes, typing claims and dependency behaviour require implementation plus validated evidence. The workflow must never mark a rule complete solely because a remediation file was generated.",
    ]
    PLAN_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_safe(plan: dict) -> list[str]:
    applied = []
    for item in plan["items"]:
        if item["execution_mode"] == "automatic":
            applied.append(item["rule_id"])
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Quality Scale workflow gate and remediation planner"
    )
    parser.add_argument(
        "command",
        choices=("status", "plan", "apply", "run", "check"),
        nargs="?",
        default="run",
    )
    args = parser.parse_args()
    config = load(CONFIG)
    run_engine()
    report = load(REPORT)
    plan = create_plan(report, config)
    write_plan(plan)
    applied = apply_safe(plan) if args.command in {"apply", "run"} else []
    status = {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "current_tier": plan["current_tier"],
        "release_minimum_tier": plan["release_minimum_tier"],
        "desired_tier": plan["desired_tier"],
        "maximum_governed_tier": plan["maximum_governed_tier"],
        "platinum_policy": plan["platinum_policy"],
        "gold_policy_verified": plan["current_tier"] == "gold" and plan["desired_tier"] == "gold" and plan["release_minimum_tier"] == "gold" and plan["maximum_governed_tier"] == "gold",
        "release_gate_status": plan["release_gate_status"],
        "desired_tier_status": plan["desired_tier_status"],
        "open_remediations": plan["open_items"],
        "automatic_remediations_applied": applied,
        "workflow_status": "PASS" if REPORT.exists() and PLAN_JSON.exists() and plan["current_tier"] == "gold" else "BLOCKED",
        "advancement_status": "ALLOWED"
        if plan["release_gate_status"] == "PASS" and plan["current_tier"] == "gold"
        else "BLOCKED",
    }
    STATUS_JSON.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(
        "Quality Scale workflow: "
        f"{status['workflow_status']} | current={status['current_tier'].upper()} | "
        f"desired={status['desired_tier'].upper()} | release={status['advancement_status']}"
    )
    return 1 if args.command == "check" and (status["advancement_status"] != "ALLOWED" or not status["gold_policy_verified"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
