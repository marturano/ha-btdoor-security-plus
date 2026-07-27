"""Home Assistant 2026.x compatibility hardening for 6.1.0-rc.4."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "custom_components" / "btdoor_security_plus"


def test_rc4_version_alignment() -> None:
    manifest = json.loads((DOMAIN / "manifest.json").read_text())
    assert manifest["version"].startswith("1.1.0-rc.")
    assert f'INTEGRATION_VERSION = "{manifest["version"]}"' in (DOMAIN / "const.py").read_text()


def test_global_actions_are_registered_in_async_setup() -> None:
    source = (DOMAIN / "__init__.py").read_text()
    setup = source[source.index("async def async_setup("):source.index("async def async_setup_entry(")]
    entry_setup = source[source.index("async def async_setup_entry("):source.index("async def async_unload_entry(")]
    assert "async_register_services(hass)" in setup
    assert "async_register_voice_intents(hass)" in setup
    assert "async_install_sentences(hass)" in setup
    assert "async_register_services(hass)" not in entry_setup
    assert "async_register_voice_intents(hass)" not in entry_setup


def test_unload_does_not_remove_integration_wide_actions() -> None:
    source = (DOMAIN / "__init__.py").read_text()
    unload = source[source.index("async def async_unload_entry("):source.index("async def _async_migrate_debug_storage(")]
    assert "async_unregister_services" not in unload
    assert "async_entries(DOMAIN)" not in unload


def test_2026_api_compatibility_guards() -> None:
    source = "\n".join(path.read_text(errors="ignore") for path in DOMAIN.rglob("*.py"))
    assert "async_forward_entry_setup(" not in source
    assert "async_setup_platforms(" not in source
    assert "entry.runtime_data" in source
    assert "SupportsResponse" in source
    assert "async_forward_entry_setups(" in source


def test_sentence_install_is_idempotent_and_requests_one_restart() -> None:
    manager = (DOMAIN / "sentence_manager.py").read_text()
    integration = (DOMAIN / "__init__.py").read_text()
    assert manager.index("if current_hash == new_hash") < manager.index("elif previous_hash and current_hash == previous_hash")
    assert "assist_sentences_restart_required" in integration
    assert 'sentence_result["installed"] or sentence_result["updated"]' in integration


def test_no_2026_6_double_reload_pattern() -> None:
    flow = (DOMAIN / "config_flow.py").read_text()
    integration = (DOMAIN / "__init__.py").read_text()
    assert "add_update_listener" in integration
    assert "async_update_reload_and_abort" not in flow
    assert "reload_on_update=True" not in flow
