"""Source-level regressions for the 6.1.0-alpha.1a local hotfix."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"


def test_call_journal_mkdir_uses_partial_for_keyword_arguments() -> None:
    source = (COMPONENT / "services.py").read_text(encoding="utf-8")
    assert "partial(export_dir.mkdir, parents=True, exist_ok=True, mode=0o700)" in source
    assert "async_add_executor_job(export_dir.mkdir, parents=True" not in source


def test_message_entities_belong_to_sip_device() -> None:
    tree = ast.parse((COMPONENT / "sensor.py").read_text(encoding="utf-8"))
    expected = {
        "BticinoLastMessageSensor",
        "BticinoMessageCountSensor",
        "BticinoLastMessageTimeSensor",
    }
    found: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in expected:
            for statement in node.body:
                if (
                    isinstance(statement, ast.Assign)
                    and any(
                        isinstance(target, ast.Name) and target.id == "_device_kind"
                        for target in statement.targets
                    )
                    and isinstance(statement.value, ast.Attribute)
                ):
                    assert statement.value.attr == "SIP"
                    found.add(node.name)
    assert found == expected


def test_options_flow_enforces_developer_dependency() -> None:
    source = (COMPONENT / "config_flow.py").read_text(encoding="utf-8")
    assert "advanced_diagnostics_requires_developer_mode" in source
    assert "normalized[CONF_SHOW_ADVANCED_DIAGNOSTICS] = False" in source
    assert "advanced_default = developer_default and bool(" in source


def test_existing_translations_include_dependency_error() -> None:
    paths = [COMPONENT / "strings.json", *(COMPONENT / "translations").glob("*.json")]
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "advanced_diagnostics_requires_developer_mode" in payload["options"]["error"], (
            path.name
        )
