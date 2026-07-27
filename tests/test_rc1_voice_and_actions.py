"""Static and isolated regression tests for 6.1.0-rc.1."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "custom_components" / "btdoor_security_plus"


def test_manifest_and_runtime_version_match() -> None:
    manifest = json.loads((DOMAIN / "manifest.json").read_text(encoding="utf-8"))
    constants = (DOMAIN / "const.py").read_text(encoding="utf-8")
    assert f'INTEGRATION_VERSION = "{manifest["version"]}"' in constants


def test_open_gate_action_has_audit_fields_and_response() -> None:
    init_source = (DOMAIN / "services.py").read_text(encoding="utf-8")
    services = yaml.safe_load((DOMAIN / "services.yaml").read_text(encoding="utf-8"))
    fields = services["open_gate"]["fields"]
    assert {"entry_id", "reason", "source"} <= set(fields)
    assert "OPEN_GATE_SCHEMA" in init_source
    assert "SupportsResponse.OPTIONAL" in init_source
    assert '"event_type": "gate_open_requested"' in init_source
    assert '"success": True' in init_source


def test_assist_sentences_and_handler_are_packaged() -> None:
    voice = (DOMAIN / "voice.py").read_text(encoding="utf-8")
    assert 'intent_type = INTENT_OPEN_GATE' in voice
    assert "len(entries) > 1" in voice
    assert '"source": "assist"' in voice
    for language in ("it", "en"):
        sentence_file = DOMAIN / "custom_sentences" / language / "btdoor_security_plus.yaml"
        payload = yaml.safe_load(sentence_file.read_text(encoding="utf-8"))
        assert payload["language"] == language
        assert "BTDoorOpenGate" in payload["intents"]
