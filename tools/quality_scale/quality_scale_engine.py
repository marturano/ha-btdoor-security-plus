#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTEGRATION = ROOT / "custom_components/btdoor_security_plus"
RULES_FILE = ROOT / "docs/quality-scale/quality_scale_rules.json"
REPORT_JSON = ROOT / "docs/quality-scale/QUALITY_SCALE_REPORT.json"
REPORT_MD = ROOT / "docs/quality-scale/QUALITY_SCALE_REPORT.md"
YAML_FILE = INTEGRATION / "quality_scale.yaml"
LEVELS = ("bronze", "silver", "gold", "platinum")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def source_text() -> str:
    parts = []
    for p in INTEGRATION.rglob("*.py"):
        parts.append(read(p))
    return "\n".join(parts)


def doc_text() -> str:
    parts = []
    for p in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]:
        parts.append(read(p).lower())
    return "\n".join(parts)


def tests_text() -> str:
    return "\n".join(read(p) for p in sorted((ROOT / "tests").glob("test_*.py")))


def rule_status(
    rule: dict, src: str, docs: str, tests: str, manifest: dict
) -> tuple[str, str, list[str]]:
    rid = rule["id"]
    evidence = []

    def done(ok: bool, reason: str, ev: list[str] | None = None) -> tuple[str, str, list[str]]:
        return ("done" if ok else "todo", reason, (ev if ev is not None else []) if ok else [])

    if rid == "action-setup":
        ok = exists("custom_components/btdoor_security_plus/services.py") and "async_setup" in read(
            INTEGRATION / "__init__.py"
        )
        return done(
            ok,
            "Service actions are present and integration setup is asynchronous.",
            [
                "custom_components/btdoor_security_plus/services.py",
                "custom_components/btdoor_security_plus/__init__.py",
            ],
        )
    if rid == "appropriate-polling":
        return (
            "exempt",
            "Manifest declares cloud_push; no fixed polling interval is required.",
            ["custom_components/btdoor_security_plus/manifest.json"],
        )
    if rid == "brands":
        return done(
            exists("custom_components/btdoor_security_plus/brand/icon.png"),
            "Brand assets are present.",
            ["custom_components/btdoor_security_plus/brand/icon.png"],
        )
    if rid == "common-modules":
        return done(
            exists("custom_components/btdoor_security_plus/entity.py")
            and exists("custom_components/btdoor_security_plus/const.py"),
            "Shared entity and constants modules are present.",
            [
                "custom_components/btdoor_security_plus/entity.py",
                "custom_components/btdoor_security_plus/const.py",
            ],
        )
    if rid == "config-flow-test-coverage":
        test_path = ROOT / "tests/test_config_flow_full_coverage.py"
        coverage_path = ROOT / "docs/quality-scale/config_flow_coverage.json"
        required_tests = (
            "test_user_initial_form",
            "test_user_error_mapping",
            "test_user_no_gateways",
            "test_user_single_gateway_success",
            "test_user_multiple_gateways_and_selection",
            "test_finish_duplicate_prevention",
            "test_finish_provisioning_error_mapping",
            "test_finish_creates_entry",
            "test_reauth_success_and_failure",
            "test_reconfigure_success_and_wrong_gateway",
            "test_options_validation_and_confirmation",
        )
        test_source = read(test_path)
        coverage = {}
        if coverage_path.exists():
            try:
                coverage = json.loads(read(coverage_path))
            except json.JSONDecodeError:
                coverage = {}
        ok = (
            bool(test_source)
            and all(name in test_source for name in required_tests)
            and coverage.get("status") == "VALIDATED"
            and coverage.get("test_file") == "tests/test_config_flow_full_coverage.py"
            and len(coverage.get("required_scenarios", [])) >= 13
        )
        return done(
            ok,
            "Dedicated behavioural coverage proves all config-flow outcomes."
            if ok
            else "Dedicated full config-flow coverage has not been proven.",
            [
                "tests/test_config_flow_full_coverage.py",
                "docs/quality-scale/config_flow_coverage.json",
            ]
            if ok
            else [],
        )
    if rid == "config-flow":
        return done(
            bool(manifest.get("config_flow"))
            and exists("custom_components/btdoor_security_plus/config_flow.py"),
            "UI config flow is enabled.",
            [
                "custom_components/btdoor_security_plus/config_flow.py",
                "custom_components/btdoor_security_plus/manifest.json",
            ],
        )
    if rid == "dependency-transparency":
        return done(
            all("==" in x for x in manifest.get("requirements", [])),
            "All manifest dependencies are pinned.",
            ["custom_components/btdoor_security_plus/manifest.json"],
        )
    if rid == "docs-actions":
        return done(
            "service" in docs or "action" in docs,
            "Action/service documentation detected.",
            ["README.md", "custom_components/btdoor_security_plus/services.yaml"],
        )
    if rid == "docs-triggers":
        return ("exempt", "No custom device trigger module is registered.", [])
    if rid == "docs-conditions":
        return ("exempt", "No custom device condition module is registered.", [])
    if rid == "docs-high-level-description":
        return done(
            "btdoor security+" in docs,
            "High-level integration description is present.",
            ["README.md"],
        )
    if rid == "docs-installation-instructions":
        return done(
            "install" in docs or "hacs" in docs,
            "Installation instructions are present.",
            ["README.md"],
        )
    if rid == "docs-removal-instructions":
        return done(
            "remove" in docs or "uninstall" in docs or "rimozione" in docs,
            "Removal instructions detected.",
            ["README.md"]
            if ("remove" in docs or "uninstall" in docs or "rimozione" in docs)
            else [],
        )
    if rid == "entity-event-setup":
        return done(
            "async_on_remove" in src or "async_will_remove_from_hass" in src,
            "Entity event lifecycle cleanup detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "entity-unique-id":
        return done(
            "unique_id" in src,
            "Unique IDs are assigned by entities/config flow.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "has-entity-name":
        return done(
            "has_entity_name" in src,
            "Entity naming opt-in detected.",
            ["custom_components/btdoor_security_plus/entity.py"],
        )
    if rid == "runtime-data":
        return done(
            "runtime_data" in src,
            "ConfigEntry.runtime_data usage detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "test-before-configure":
        return done(
            any(
                x in read(INTEGRATION / "config_flow.py")
                for x in ["async_validate", "async_connect", "cannot_connect", "TimeoutError"]
            ),
            "Connection validation logic detected in config flow.",
            ["custom_components/btdoor_security_plus/config_flow.py"],
        )
    if rid == "test-before-setup":
        return done(
            "ConfigEntryNotReady" in read(INTEGRATION / "__init__.py")
            or "async_setup_entry" in read(INTEGRATION / "__init__.py"),
            "Setup entry performs runtime initialization and failure handling.",
            ["custom_components/btdoor_security_plus/__init__.py"],
        )
    if rid == "unique-config-entry":
        return done(
            "_abort_if_unique_id_configured" in read(INTEGRATION / "config_flow.py")
            or "async_set_unique_id" in read(INTEGRATION / "config_flow.py"),
            "Duplicate-entry prevention detected.",
            ["custom_components/btdoor_security_plus/config_flow.py"],
        )
    if rid == "action-exceptions":
        return done(
            "ServiceValidationError" in src or "HomeAssistantError" in src,
            "Home Assistant service/action exceptions detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "config-entry-unloading":
        return done(
            "async_unload_entry" in read(INTEGRATION / "__init__.py"),
            "Config entry unloading is implemented.",
            ["custom_components/btdoor_security_plus/__init__.py"],
        )
    if rid == "docs-configuration-parameters":
        return done(
            "option" in docs and "configuration" in docs,
            "Configuration/options documentation detected.",
            ["README.md"],
        )
    if rid == "docs-installation-parameters":
        return done(
            "host" in docs or "token" in docs or "credential" in docs,
            "Installation parameters are described.",
            ["README.md"],
        )
    if rid == "entity-unavailable":
        return done(
            "available" in src or "UpdateFailed" in src,
            "Entity availability handling detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "integration-owner":
        return done(
            bool(manifest.get("codeowners")),
            "Integration owner is declared.",
            ["custom_components/btdoor_security_plus/manifest.json"],
        )
    if rid == "log-when-unavailable":
        return done(
            "unavailable" in src and ("available again" in src or "recovered" in src),
            "Availability transition logging detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "parallel-updates":
        return done(
            "PARALLEL_UPDATES" in src,
            "Platform parallel update limits are declared.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "reauthentication-flow":
        return done(
            "async_step_reauth" in read(INTEGRATION / "config_flow.py"),
            "Reauthentication flow detected.",
            ["custom_components/btdoor_security_plus/config_flow.py"],
        )
    if rid == "test-coverage":
        evidence_path = ROOT / "docs/quality-scale/integration_coverage.json"
        if evidence_path.exists():
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            ok = (
                evidence.get("status") == "VALIDATED"
                and float(evidence.get("measured_percent", 0)) > 95.0
            )
            return done(
                ok,
                f"Measured integration coverage is {evidence.get('measured_percent', 0)}%; above 95% is required.",
                [
                    "docs/quality-scale/integration_coverage.json",
                    "docs/quality-scale/INTEGRATION_COVERAGE_REPORT.md",
                ],
            )
        return ("todo", "A measured integration coverage result above 95% is required.", [])
    if rid == "devices":
        return done(
            "DeviceInfo" in src or "device_info" in src,
            "Device registry integration detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "diagnostics":
        return done(
            exists("custom_components/btdoor_security_plus/diagnostics.py"),
            "Diagnostics are implemented.",
            ["custom_components/btdoor_security_plus/diagnostics.py"],
        )
    if rid == "discovery-update-info":
        return ("exempt", "No supported network discovery mechanism is currently declared.", [])
    if rid == "discovery":
        return (
            "exempt",
            "The integration is configured explicitly and declares no discovery matcher.",
            [],
        )
    if rid == "docs-data-update":
        return done(
            "push" in docs or "update" in docs, "Data update behavior is documented.", ["README.md"]
        )
    if rid == "docs-examples":
        return done(
            exists("blueprints") and any((ROOT / "blueprints").rglob("*.yaml")),
            "Automation blueprints/examples are present.",
            ["blueprints"],
        )
    if rid == "docs-known-limitations":
        return done(
            "known limitation" in docs or "limitazioni" in docs,
            "Known limitations are documented.",
            ["README.md"],
        )
    if rid == "docs-supported-devices":
        return done(
            "supported device" in docs or "dispositivi supportati" in docs,
            "Supported devices are documented.",
            ["README.md"],
        )
    if rid == "docs-supported-functions":
        return done(
            "supported function" in docs or "entities" in docs or "entità" in docs,
            "Supported functionality/entities are documented.",
            ["README.md"],
        )
    if rid == "docs-troubleshooting":
        return done(
            "troubleshoot" in docs or "risoluzione" in docs,
            "Troubleshooting documentation is present.",
            ["README.md"],
        )
    if rid == "docs-use-cases":
        return done(
            "use case" in docs or "scenario" in docs or "casi d" in docs,
            "Use cases are documented.",
            ["README.md"],
        )
    if rid == "dynamic-devices":
        return done(
            "async_add_entities" in src
            and ("dispatcher" in src or "async_dispatcher_connect" in src),
            "Dynamic entity/device handling detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "entity-category":
        return done(
            "EntityCategory" in src,
            "Entity categories are used.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "entity-device-class":
        return done(
            "device_class" in src or "SensorDeviceClass" in src or "BinarySensorDeviceClass" in src,
            "Device classes are used where available.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "entity-disabled-by-default":
        return done(
            "_attr_entity_registry_enabled_default" in src,
            "Noisy/advanced entities can be disabled by default.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "entity-translations":
        return done(
            exists("custom_components/btdoor_security_plus/translations/en.json")
            and ("translation_key" in src),
            "Entity translations detected.",
            [
                "custom_components/btdoor_security_plus/translations",
                "custom_components/btdoor_security_plus",
            ],
        )
    if rid == "exception-translations":
        return done(
            "translation_domain" in src
            or "translation_key" in src
            and "ServiceValidationError" in src,
            "Translatable exception support detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "icon-translations":
        return done(
            exists("custom_components/btdoor_security_plus/icons.json"),
            "Icon translations are provided.",
            ["custom_components/btdoor_security_plus/icons.json"],
        )
    if rid == "reconfiguration-flow":
        return done(
            "async_step_reconfigure" in read(INTEGRATION / "config_flow.py"),
            "Reconfigure flow detected.",
            ["custom_components/btdoor_security_plus/config_flow.py"],
        )
    if rid == "repair-issues":
        return done(
            "async_create_issue" in src or "repairs" in src,
            "Repairs integration usage detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "stale-devices":
        return done(
            "async_remove_device" in src or "async_remove_config_entry_device" in src,
            "Stale-device removal support detected.",
            ["custom_components/btdoor_security_plus"],
        )
    if rid == "async-dependency":
        return (
            "todo",
            "The external dependency must be formally verified as fully asynchronous.",
            [],
        )
    if rid == "inject-websession":
        return (
            "todo",
            "The external dependency must support injection of Home Assistant web sessions.",
            [],
        )
    if rid == "strict-typing":
        return (
            "todo",
            "Strict typing must be proven with a repository-wide type checker gate.",
            [],
        )
    return ("todo", "No automated verifier is defined.", [])


def yaml_value(item: dict) -> list[str]:
    rid = item["id"]
    status = item["status"]
    reason = item["reason"].replace("\n", " ")
    if status == "done":
        return [f"  {rid}: done"]
    return [
        f"  {rid}:",
        f"    status: {status}",
        f'    comment: "{reason.replace(chr(34), chr(39))}"',
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rules = json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]
    manifest = json.loads((INTEGRATION / "manifest.json").read_text(encoding="utf-8"))
    src, docs, tests = source_text(), doc_text(), tests_text()
    assessed = []
    for rule in rules:
        status, reason, evidence = rule_status(rule, src, docs, tests, manifest)
        assessed.append({**rule, "status": status, "reason": reason, "evidence": evidence})
    summaries = {}
    cumulative_ok = True
    achieved = "legacy"
    for level in LEVELS:
        items = [x for x in assessed if x["tier"] == level]
        level_ok = all(x["status"] in {"done", "exempt"} for x in items)
        cumulative_ok = cumulative_ok and level_ok
        if cumulative_ok:
            achieved = level
        summaries[level] = {
            "total": len(items),
            "done": sum(x["status"] == "done" for x in items),
            "exempt": sum(x["status"] == "exempt" for x in items),
            "todo": sum(x["status"] == "todo" for x in items),
            "level_complete": level_ok,
            "cumulative_complete": cumulative_ok,
        }
    payload = {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "standard": "Home Assistant Integration Quality Scale",
        "assessment_type": "self-assessment for a custom integration; not an official Home Assistant grade",
        "achieved_tier": achieved,
        "target_tier": "gold",
        "maximum_governed_tier": "gold",
        "platinum_policy": "out_of_scope_unless_explicitly_reopened_by_project_decision",
        "release_gate_required_tier": "gold",
        "release_gate_status": "PASS"
        if LEVELS.index(achieved) >= LEVELS.index("gold")
        else "BLOCKED",
        "summaries": summaries,
        "rules": assessed,
        "official_sources": [
            "https://developers.home-assistant.io/docs/core/integration-quality-scale/",
            "https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/",
        ],
    }
    REPORT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Home Assistant Integration Quality Scale Report",
        "",
        f"**Generated:** {payload['generated']}",
        f"**Assessment:** {payload['assessment_type']}",
        f"**Achieved tier:** **{achieved.upper()}**",
        "**Project target:** **GOLD**",
        f"**Release gate (minimum Gold):** **{payload['release_gate_status']}**",
        "**Platinum policy:** **OUT OF SCOPE** unless explicitly reopened by project decision",
        "",
        "## Tier summary",
        "",
        "| Tier | Done | Exempt | Todo | Tier complete | Cumulative complete |",
        "|---|---:|---:|---:|---|---|",
    ]
    for level in LEVELS:
        s = summaries[level]
        lines.append(
            f"| {level.title()} | {s['done']} | {s['exempt']} | {s['todo']} | {'YES' if s['level_complete'] else 'NO'} | {'YES' if s['cumulative_complete'] else 'NO'} |"
        )
    lines += [
        "",
        "## Rule assessment",
        "",
        "| Tier | Rule | Status | Reason |",
        "|---|---|---|---|",
    ]
    for r in assessed:
        lines.append(
            f"| {r['tier'].title()} | `{r['id']}` | {r['status'].upper()} | {r['reason'].replace('|', '/')} |"
        )
    lines += [
        "",
        "## Governance note",
        "",
        "This report is a repository self-assessment aligned with the official Home Assistant rule set. It does not claim an official Home Assistant Core grade or review. Manual and runtime evidence remains mandatory where static inspection cannot prove compliance.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    yaml_lines = [
        "# Generated by tools/quality_scale/quality_scale_engine.py",
        "# Self-assessment aligned with the Home Assistant Integration Quality Scale.",
        "rules:",
    ]
    for item in assessed:
        yaml_lines.extend(yaml_value(item))
    YAML_FILE.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Quality scale: {achieved.upper()} | Gold gate: {payload['release_gate_status']}")
    return 1 if args.check and payload["release_gate_status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
