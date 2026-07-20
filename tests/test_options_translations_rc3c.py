"""Regression tests for rc.3c custom-integration translations."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1] / "custom_components" / "btdoor_security_plus"
OPTION_KEYS = {
    "show_cloud_status",
    "show_sip_monitor",
    "show_call_monitor",
    "show_media_monitor",
    "show_advanced_diagnostics",
    "developer_mode",
    "debug_mode",
}
DEBUG_OPTIONS = {"off", "support", "deep"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_complete_english_catalog_exists() -> None:
    """Custom integrations require a complete translations/en.json catalog."""
    assert _load(ROOT / "translations" / "en.json") == _load(ROOT / "strings.json")


def test_options_have_names_and_descriptions_in_all_catalogs() -> None:
    """Every options-flow field must have a label and a description."""
    for path in sorted((ROOT / "translations").glob("*.json")):
        step = _load(path)["options"]["step"]["init"]
        assert OPTION_KEYS <= set(step["data"]), path.name
        assert OPTION_KEYS <= set(step["data_description"]), path.name


def test_debug_selector_values_are_translated() -> None:
    """The selector must not expose raw values or hard-coded English labels."""
    for path in [ROOT / "strings.json", *(ROOT / "translations").glob("*.json")]:
        options = _load(path)["selector"]["debug_mode"]["options"]
        assert DEBUG_OPTIONS == set(options), path.name
        assert all(options[value].strip() for value in DEBUG_OPTIONS), path.name


def test_config_flow_uses_selector_translation_key() -> None:
    source = (ROOT / "config_flow.py").read_text(encoding="utf-8")
    assert "translation_key=CONF_DEBUG_MODE" in source
    assert '"label": "Disabled"' not in source
    assert '"label": "Deep debug"' not in source
