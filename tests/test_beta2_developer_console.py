"""Regression tests for 6.1.0-beta.2 dashboards and Developer Console."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PKG = "custom_components.btdoor_security_plus"


def _load(name: str, path: Path):
    for package in ("custom_components", PKG, f"{PKG}.ux"):
        if package not in sys.modules:
            module = types.ModuleType(package)
            module.__path__ = [str(ROOT / package.replace(".", "/"))]
            sys.modules[package] = module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


resolver = _load(
    f"{PKG}.ux.entity_resolver",
    ROOT / "custom_components/btdoor_security_plus/ux/entity_resolver.py",
)
builder_module = _load(
    f"{PKG}.ux.dashboard_builder",
    ROOT / "custom_components/btdoor_security_plus/ux/dashboard_builder.py",
)


def _entity(unique_id: str, entity_id: str):
    return types.SimpleNamespace(unique_id=unique_id, entity_id=entity_id, config_entry_id="entry")


def test_runtime_dashboard_has_no_developer_dependencies():
    text = (ROOT / "dashboards/templates/runtime-dashboard.yaml").read_text()
    assert "developer_runtime_inspector" not in text
    assert "generate_support_report" not in text
    yaml.safe_load(text)


def test_developer_console_resolves_all_nested_targets():
    entries = [
        _entity("door_developer_runtime_inspector", "sensor.runtime_inspector"),
        _entity("door_developer_event_monitor", "sensor.event_monitor"),
        _entity("door_developer_event_metrics", "sensor.event_metrics"),
        _entity("door_run_developer_test", "button.run_tests"),
        _entity("door_generate_support_report", "button.support_bundle"),
        _entity("door_clean_debug_environment", "button.clean_debug"),
    ]
    entity_map = resolver.DashboardEntityResolver.resolve(entries, config_entry_id="entry")
    result = builder_module.DashboardBuilder(ROOT / "dashboards/templates").build(
        "developer-console.yaml", entity_map
    )
    assert result.missing_entities == ()
    assert "btdoor_template_" not in result.content
    assert "__ENTITY_" not in result.content
    assert result.content.count("button.run_tests") >= 2
    assert result.content.count("button.support_bundle") >= 2
    yaml.safe_load(result.content)


def test_voice_assistant_and_console_docs_exist_in_all_locales():
    for locale in ("en", "it", "fr", "de", "es", "nl"):
        assert (ROOT / "docs" / locale / "developer_console.md").is_file()
        assert (ROOT / "docs" / locale / "voice_assistants.md").is_file()
