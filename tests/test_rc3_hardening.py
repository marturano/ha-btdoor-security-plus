"""Release hardening regressions for 6.1.0-rc.3."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "custom_components" / "btdoor_security_plus"
LANGUAGES = {
    "en",
    "it",
    "fr",
    "de",
    "es",
    "nl",
    "pt",
    "pl",
    "cs",
    "da",
    "sv",
    "nb",
    "fi",
    "ja",
    "ko",
    "zh-Hans",
    "zh-Hant",
}


def test_version_alignment():
    manifest = json.loads((DOMAIN / "manifest.json").read_text())
    assert manifest["version"].startswith("1.1.0-rc.")
    assert f'INTEGRATION_VERSION = "{manifest["version"]}"' in (DOMAIN / "const.py").read_text()


def test_global_service_manager_is_entry_independent_and_symmetric():
    source = (DOMAIN / "services.py").read_text()
    assert "REGISTERED_SERVICES" in source
    assert "async_unregister_services" in source
    assert "require_single=True" in source
    assert 'translation_key="multiple_gates"' in source
    assert "runtime.debug.record" in source
    assert "debug.record(" not in source.replace("runtime.debug.record", "")


def test_gate_action_timeout_and_audit_completion_events():
    source = (DOMAIN / "services.py").read_text()
    assert "asyncio.timeout(OPEN_GATE_TIMEOUT)" in source
    assert "gate_open_requested" in source
    assert "gate_open_succeeded" in source
    assert "gate_open_failed" in source
    assert "request_id" in source and "duration_ms" in source


def test_call_journal_export_is_private():
    source = (DOMAIN / "services.py").read_text()
    assert 'hass.config.path(DOMAIN, "exports")' in source
    assert '"private": True' in source
    assert "/local/" not in source
    assert "0o600" in source


def test_sentence_manager_preserves_user_edits():
    source = (DOMAIN / "sentence_manager.py").read_text()
    assert "previous_hash" in source and "current_hash == previous_hash" in source
    assert "preserved += 1" in source
    assert "custom_sentences" in source


def test_assist_uses_service_response():
    source = (DOMAIN / "voice.py").read_text()
    assert "return_response=True" in source
    assert 'item.get("success")' in source


def test_translation_key_parity_for_all_voice_languages():
    base = json.loads((DOMAIN / "translations/en.json").read_text())

    def leaves(value, prefix=""):
        if isinstance(value, dict):
            out = set()
            for key, item in value.items():
                out |= leaves(item, f"{prefix}.{key}" if prefix else key)
            return out
        return {prefix}

    expected = leaves(base)
    for language in LANGUAGES:
        payload = json.loads((DOMAIN / "translations" / f"{language}.json").read_text())
        assert leaves(payload) == expected
