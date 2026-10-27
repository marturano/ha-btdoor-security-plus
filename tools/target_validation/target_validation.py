#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/target-validation"
WORK = ROOT / "target-validation-work"
RUNS = BASE / "runs"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

REQUIRED = {
    "runtime": [
        "startup_seconds",
        "reload_seconds",
        "memory_delta_mb",
        "sustained_observation_minutes",
    ],
    "compatibility": [
        "clean_setup",
        "restart_recovery",
        "entity_continuity",
        "diagnostics_export",
    ],
    "hacs_lifecycle": ["clean_install", "upgrade", "rollback"],
    "security": [
        "secret_handling",
        "log_redaction",
        "permissions",
        "dependency_review",
    ],
    "ux_accessibility": [
        "dashboard_review",
        "keyboard_review",
        "contrast_review",
        "localization_review",
    ],
}

EVIDENCE_IDS = {
    "runtime": "EV-PERF-002",
    "compatibility": "EV-COMP-001",
    "hacs_lifecycle": "EV-PUB-001",
    "security": "EV-SEC-002",
    "ux_accessibility": "EV-UX-001",
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def validate_run_id(run_id: str) -> str:
    if not RUN_ID_PATTERN.fullmatch(run_id) or run_id in {".", ".."} or ".." in run_id:
        raise SystemExit(
            "Invalid run id; use 1-128 letters, numbers, dots, underscores, or hyphens "
            "without path separators or '..'"
        )
    return run_id


def run_dir(run_id: str) -> Path:
    return WORK / validate_run_id(run_id)


def load_result(run_id: str) -> tuple[Path, dict]:
    path = run_dir(run_id) / "result.json"
    if not path.exists():
        raise SystemExit(f"Missing {path}; run init first")
    return path, json.loads(path.read_text(encoding="utf-8"))


def checklist_text(data: dict) -> str:
    lines = [
        f"# Target validation checklist — {data['run_id']}",
        "",
        f"Created: `{data['created_at']}`",
        "",
        "Use `PASS`, `FAIL`, or `NOT_RUN` in field notes. Set JSON checks to "
        "`VALIDATED` only after attaching sanitized evidence.",
        "",
    ]
    for section, checks in REQUIRED.items():
        lines.extend(
            [
                f"## {section.replace('_', ' ').title()} — {EVIDENCE_IDS[section]}",
                "",
            ]
        )
        for check in checks:
            lines.append(f"- [ ] `{check}` — evidence: ____________________")
        lines.extend(["", "Operator notes:", "", "---", ""])
    lines.extend(
        [
            "## Final attestation",
            "",
            "- [ ] Home Assistant version recorded",
            "- [ ] installation type recorded",
            "- [ ] all evidence is sanitized",
            "- [ ] every required check is VALIDATED",
            "- [ ] operator name, date and statement completed",
            "- [ ] `validate` returns PASS",
            "- [ ] accepted run imported immutably",
            "",
        ]
    )
    return "\n".join(lines)


def init(run_id: str) -> None:
    directory = run_dir(run_id)
    if directory.exists():
        raise SystemExit(f"Run already exists: {run_id}")
    (directory / "evidence").mkdir(parents=True)
    sections = {
        name: {
            "evidence_id": EVIDENCE_IDS[name],
            "status": "PENDING",
            "checks": {
                key: {
                    "status": "PENDING",
                    "value": None,
                    "unit": "",
                    "notes": "",
                    "evidence": [],
                }
                for key in checks
            },
        }
        for name, checks in REQUIRED.items()
    }
    data = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": utc_now(),
        "environment": {
            "home_assistant_version": "",
            "installation_type": "",
            "host": "",
            "integration_version": "1.1.0-rc.15",
        },
        "automatic_collection": {"status": "PENDING"},
        "sections": sections,
        "evidence_files": [],
        "operator_attestation": {"name": "", "date": "", "statement": ""},
        "import_status": "NOT_IMPORTED",
    }
    (directory / "result.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (directory / "CHECKLIST.md").write_text(checklist_text(data), encoding="utf-8")
    (directory / "README.md").write_text(
        f"# Target validation run {run_id}\n\n"
        "1. Follow `CHECKLIST.md`.\n"
        "2. Complete `result.json`.\n"
        "3. Store only sanitized evidence in `evidence/`.\n"
        "4. Run `status`, then `validate`, then `import`.\n",
        encoding="utf-8",
    )
    print(directory)


def api_get(url: str, token: str, path: str) -> object:
    request = urllib.request.Request(
        url.rstrip("/") + path,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode())


def safe_host_label(url: str) -> str:
    parsed = urlsplit(url if "://" in url else f"http://{url}")
    return parsed.hostname or "home-assistant-target"


def collect(run_id: str) -> None:
    url = os.environ.get("HA_URL", "").strip()
    token = os.environ.get("HA_TOKEN", "").strip()
    if not url or not token:
        raise SystemExit("HA_URL and HA_TOKEN are required")
    path, data = load_result(run_id)
    config = api_get(url, token, "/api/config")
    states = api_get(url, token, "/api/states")
    if not isinstance(config, dict) or not isinstance(states, list):
        raise SystemExit("Unexpected Home Assistant API response")
    integration = [
        state
        for state in states
        if "btdoor" in state.get("entity_id", "").lower()
        or "btdoor" in json.dumps(state.get("attributes", {})).lower()
    ]
    unavailable = [
        state["entity_id"]
        for state in integration
        if state.get("state") in {"unavailable", "unknown"}
    ]
    summary = {
        "collected_at": utc_now(),
        "home_assistant_version": config.get("version", ""),
        "installation_type": config.get("installation_type", "unknown"),
        "location_name": config.get("location_name", ""),
        "integration_entity_count": len(integration),
        "unavailable_entities": unavailable,
    }
    evidence = run_dir(run_id) / "evidence" / "automatic_collection.json"
    evidence.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    data["environment"].update(
        {
            "home_assistant_version": summary["home_assistant_version"],
            "installation_type": summary["installation_type"],
            "host": safe_host_label(url),
        }
    )
    data["automatic_collection"] = {
        "status": "COLLECTED",
        "evidence": "evidence/automatic_collection.json",
    }
    if "evidence/automatic_collection.json" not in data["evidence_files"]:
        data["evidence_files"].append("evidence/automatic_collection.json")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


def safe_evidence_path(base: Path, relative: str) -> Path | None:
    if not relative or Path(relative).is_absolute():
        return None
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError:
        return None
    return candidate


def validate_data(base: Path, data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not data.get("run_id"):
        errors.append("run_id missing")
    elif str(data.get("run_id")) != base.name:
        errors.append("run_id does not match the run directory")
    environment = data.get("environment", {})
    for key in ("home_assistant_version", "installation_type", "host"):
        if not str(environment.get(key, "")).strip():
            errors.append(f"environment.{key} missing")
    version = str(environment.get("home_assistant_version", ""))
    if version and not version.startswith("2026."):
        errors.append("target Home Assistant version must be within the supported 2026.x series")
    sections = data.get("sections", {})
    for name, required in REQUIRED.items():
        section = sections.get(name)
        if not isinstance(section, dict):
            errors.append(f"section {name} missing")
            continue
        if section.get("evidence_id") != EVIDENCE_IDS[name]:
            errors.append(f"section {name} evidence_id mismatch")
        checks = section.get("checks", {})
        for key in required:
            item = checks.get(key)
            if not isinstance(item, dict):
                errors.append(f"{name}.{key} missing")
                continue
            if item.get("status") != "VALIDATED":
                errors.append(f"{name}.{key} not VALIDATED")
            evidence_paths = item.get("evidence", [])
            if not evidence_paths:
                errors.append(f"{name}.{key} has no evidence")
            for relative in evidence_paths:
                evidence_file = safe_evidence_path(base, relative)
                if evidence_file is None:
                    errors.append(f"unsafe evidence path: {relative}")
                elif not evidence_file.is_file():
                    errors.append(f"missing evidence file: {relative}")
        if section.get("status") != "VALIDATED":
            errors.append(f"section {name} not VALIDATED")
    for relative in data.get("evidence_files", []):
        evidence_file = safe_evidence_path(base, relative)
        if evidence_file is None:
            errors.append(f"unsafe declared evidence path: {relative}")
        elif not evidence_file.is_file():
            errors.append(f"missing declared evidence file: {relative}")
    attestation = data.get("operator_attestation", {})
    for key in ("name", "date", "statement"):
        if not str(attestation.get(key, "")).strip():
            errors.append(f"operator_attestation.{key} missing")
    return errors


def status(run_id: str) -> None:
    path, data = load_result(run_id)
    completed = 0
    total = sum(len(checks) for checks in REQUIRED.values())
    sections = {}
    for name, required in REQUIRED.items():
        checks = data.get("sections", {}).get(name, {}).get("checks", {})
        count = sum(checks.get(key, {}).get("status") == "VALIDATED" for key in required)
        completed += count
        sections[name] = {"validated": count, "required": len(required)}
    errors = validate_data(path.parent, data)
    print(
        json.dumps(
            {
                "run_id": run_id,
                "validated_checks": completed,
                "required_checks": total,
                "sections": sections,
                "target_series": "2026.x",
                "reference_target": str(
                    data.get("environment", {}).get("home_assistant_version", "")
                ).startswith("2026.7."),
                "ready_for_import": not errors,
                "blocking_items": errors,
            },
            indent=2,
        )
    )


def validate(run_id: str, json_output: bool = False) -> bool:
    path, data = load_result(run_id)
    errors = validate_data(path.parent, data)
    output = {"run_id": run_id, "status": "PASS" if not errors else "FAIL", "errors": errors}
    print(
        json.dumps(output, indent=2)
        if json_output
        else ("PASS" if not errors else "\n".join(["FAIL"] + ["- " + error for error in errors]))
    )
    return not errors


def import_run(run_id: str) -> None:
    path, data = load_result(run_id)
    errors = validate_data(path.parent, data)
    if errors:
        raise SystemExit("Run rejected:\n" + "\n".join("- " + error for error in errors))
    destination = RUNS / run_id
    if destination.exists():
        raise SystemExit("Imported run is immutable; use a new run id")
    data["import_status"] = "ACCEPTED"
    data["imported_at"] = utc_now()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    shutil.copytree(path.parent, destination)
    print(destination)


def latest() -> None:
    accepted = []
    for path in RUNS.glob("*/result.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("import_status") == "ACCEPTED":
                accepted.append((data.get("imported_at", ""), path, data))
        except (OSError, json.JSONDecodeError):
            continue
    if not accepted:
        print(json.dumps({"status": "NONE"}))
        return
    _, path, data = max(accepted, key=lambda item: item[0])
    print(
        json.dumps(
            {
                "status": "FOUND",
                "path": str(path.relative_to(ROOT)),
                "run_id": data["run_id"],
            },
            indent=2,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "collect", "status", "validate", "import"):
        command = subparsers.add_parser(name)
        command.add_argument("--run-id", required=True)
        if name == "validate":
            command.add_argument("--json", action="store_true")
    subparsers.add_parser("latest")
    args = parser.parse_args()
    if args.command == "init":
        init(args.run_id)
    elif args.command == "collect":
        collect(args.run_id)
    elif args.command == "status":
        status(args.run_id)
    elif args.command == "validate":
        return 0 if validate(args.run_id, args.json) else 1
    elif args.command == "import":
        import_run(args.run_id)
    elif args.command == "latest":
        latest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
