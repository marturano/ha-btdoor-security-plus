#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/home-assistant-certification"
WORK = ROOT / "ha-certification-work"
REQUIRED_SCENARIOS = (
    "api_connectivity",
    "integration_loaded",
    "entity_inventory",
    "restart_recovery",
    "config_entry_continuity",
    "diagnostics_export",
    "service_smoke_test",
    "log_review",
    "backup_created",
    "upgrade_evidence",
    "rollback_evidence",
    "operator_review",
)


def now():
    return datetime.now(UTC).isoformat()


def run_dir(run_id: str) -> Path:
    return WORK / run_id


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(run_id: str):
    p = run_dir(run_id) / "certification.json"
    if not p.exists():
        raise SystemExit(f"Missing {p}; run init first")
    return p, json.loads(p.read_text(encoding="utf-8"))


def init(run_id: str) -> None:
    d = run_dir(run_id)
    if d.exists():
        raise SystemExit(f"Run already exists: {run_id}")
    (d / "evidence").mkdir(parents=True)
    scenarios = {
        name: {"status": "PENDING", "notes": "", "evidence": []} for name in REQUIRED_SCENARIOS
    }
    data = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": now(),
        "environment": {
            "home_assistant_url": "",
            "home_assistant_version": "",
            "installation_type": "",
            "host": "",
        },
        "probe": {"status": "PENDING"},
        "scenarios": scenarios,
        "operator_attestation": {"name": "", "date": "", "statement": ""},
        "status": "DRAFT",
    }
    write_json(d / "certification.json", data)
    (d / "README.md").write_text(
        "# Home Assistant certification run\n\nUse `probe`, complete manual scenarios, then run `validate` and `export-target`.\n",
        encoding="utf-8",
    )
    print(d)


def api_get(url: str, token: str, path: str):
    req = urllib.request.Request(
        url.rstrip("/") + path,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def probe(run_id: str) -> None:
    url = os.environ.get("HA_URL", "").strip()
    token = os.environ.get("HA_TOKEN", "").strip()
    if not url or not token:
        raise SystemExit("HA_URL and HA_TOKEN are required")
    p, data = load(run_id)
    started = time.perf_counter()
    try:
        config = api_get(url, token, "/api/config")
        states = api_get(url, token, "/api/states")
    except (urllib.error.URLError, TimeoutError) as err:
        raise SystemExit(f"Home Assistant API probe failed: {err}") from err
    elapsed = round(time.perf_counter() - started, 3)
    entities = [
        s
        for s in states
        if "btdoor" in s.get("entity_id", "").lower()
        or "btdoor" in json.dumps(s.get("attributes", {})).lower()
    ]
    unavailable = [
        s.get("entity_id") for s in entities if s.get("state") in {"unknown", "unavailable"}
    ]
    summary = {
        "collected_at": now(),
        "api_roundtrip_seconds": elapsed,
        "home_assistant_version": config.get("version", ""),
        "installation_type": config.get("installation_type", "unknown"),
        "entity_count": len(entities),
        "unavailable_entities": unavailable,
        "integration_detected": bool(entities),
    }
    write_json(run_dir(run_id) / "evidence" / "api_probe.json", summary)
    data["environment"].update(
        {
            "home_assistant_url": url,
            "home_assistant_version": summary["home_assistant_version"],
            "installation_type": summary["installation_type"],
            "host": url.split("://", 1)[-1].split("/", 1)[0],
        }
    )
    data["probe"] = {
        "status": "COLLECTED",
        "evidence": ["evidence/api_probe.json"],
        "summary": summary,
    }
    for name in ("api_connectivity", "entity_inventory"):
        data["scenarios"][name] = {
            "status": "VALIDATED",
            "notes": "Collected automatically through authenticated Home Assistant API.",
            "evidence": ["evidence/api_probe.json"],
        }
    if summary["integration_detected"]:
        data["scenarios"]["integration_loaded"] = {
            "status": "VALIDATED",
            "notes": "BTDoor entities detected through Home Assistant state API.",
            "evidence": ["evidence/api_probe.json"],
        }
    write_json(p, data)
    print(json.dumps(summary, indent=2))


def validation_errors(base: Path, data: dict) -> list[str]:
    errors = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    env = data.get("environment", {})
    for key in ("home_assistant_url", "home_assistant_version", "installation_type", "host"):
        if not str(env.get(key, "")).strip():
            errors.append(f"environment.{key} missing")
    version = str(env.get("home_assistant_version", ""))
    if version and not version.startswith("2026."):
        errors.append("Home Assistant version must be 2026.x")
    scenarios = data.get("scenarios", {})
    for name in REQUIRED_SCENARIOS:
        item = scenarios.get(name)
        if not isinstance(item, dict):
            errors.append(f"scenario {name} missing")
            continue
        if item.get("status") != "VALIDATED":
            errors.append(f"{name} not VALIDATED")
        if not str(item.get("notes", "")).strip():
            errors.append(f"{name} notes missing")
        evidence = item.get("evidence", [])
        if not evidence:
            errors.append(f"{name} evidence missing")
        for rel in evidence:
            if not (base / rel).is_file():
                errors.append(f"missing evidence file: {rel}")
    att = data.get("operator_attestation", {})
    for key in ("name", "date", "statement"):
        if not str(att.get(key, "")).strip():
            errors.append(f"operator_attestation.{key} missing")
    return errors


def validate(run_id: str, json_output: bool = False) -> bool:
    p, data = load(run_id)
    errors = validation_errors(p.parent, data)
    out = {"run_id": run_id, "status": "PASS" if not errors else "FAIL", "errors": errors}
    print(
        json.dumps(out, indent=2)
        if json_output
        else ("PASS" if not errors else "FAIL\n" + "\n".join("- " + e for e in errors))
    )
    return not errors


def export_target(run_id: str) -> None:
    p, data = load(run_id)
    errors = validation_errors(p.parent, data)
    if errors:
        raise SystemExit("Certification rejected:\n" + "\n".join("- " + e for e in errors))
    mapping = {
        "runtime": ["api_connectivity", "integration_loaded", "restart_recovery"],
        "compatibility": ["entity_inventory", "config_entry_continuity", "diagnostics_export"],
        "hacs_lifecycle": ["backup_created", "upgrade_evidence", "rollback_evidence"],
        "security": ["log_review", "service_smoke_test"],
        "ux_accessibility": ["operator_review"],
    }
    sections = {}
    for section, names in mapping.items():
        checks = {}
        for name in names:
            source = data["scenarios"][name]
            checks[name] = {
                "status": "VALIDATED",
                "notes": source["notes"],
                "evidence": source["evidence"],
            }
        sections[section] = {"status": "VALIDATED", "checks": checks}
    target = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": data["created_at"],
        "environment": {
            "home_assistant_version": data["environment"]["home_assistant_version"],
            "installation_type": data["environment"]["installation_type"],
            "host": data["environment"]["host"],
        },
        "automatic_collection": data["probe"],
        "sections": sections,
        "evidence_files": sorted(
            {rel for item in data["scenarios"].values() for rel in item.get("evidence", [])}
        ),
        "operator_attestation": data["operator_attestation"],
        "import_status": "NOT_IMPORTED",
    }
    out = run_dir(run_id) / "target-validation-result.json"
    write_json(out, target)
    print(out)


def status() -> None:
    print(
        json.dumps(
            {
                "status": "READY",
                "required_scenarios": len(REQUIRED_SCENARIOS),
                "requires_live_home_assistant": True,
                "supported_target": "Home Assistant 2026.x",
            },
            indent=2,
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("init", "probe", "validate", "export-target"):
        p = sub.add_parser(name)
        p.add_argument("--run-id", required=True)
        if name == "validate":
            p.add_argument("--json", action="store_true")
    sub.add_parser("status")
    args = ap.parse_args()
    if args.command == "init":
        init(args.run_id)
    elif args.command == "probe":
        probe(args.run_id)
    elif args.command == "validate":
        return 0 if validate(args.run_id, args.json) else 1
    elif args.command == "export-target":
        export_target(args.run_id)
    else:
        status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
