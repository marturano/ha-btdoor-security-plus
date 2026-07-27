"""QS-21 behavioural evidence for translated user-facing exceptions."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "btdoor_security_plus"
EXPECTED = {
    "no_matching_config",
    "multiple_gates",
    "sip_connection_test_failed",
    "call_rejection_failed",
    "developer_mode_disabled",
    "gate_open_failed",
}


def test_all_exception_keys_exist_in_source_strings() -> None:
    strings = json.loads((INTEGRATION / "strings.json").read_text(encoding="utf-8"))
    assert set(strings["exceptions"]) == EXPECTED
    assert all(item.get("message") for item in strings["exceptions"].values())


def test_all_supported_translations_have_exception_key_parity() -> None:
    for path in sorted((INTEGRATION / "translations").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert set(data.get("exceptions", {})) == EXPECTED, path.name
        assert all(item.get("message") for item in data["exceptions"].values()), path.name


def test_runtime_raises_translation_key_based_exceptions() -> None:
    source = "\n".join(
        (INTEGRATION / name).read_text(encoding="utf-8")
        for name in ("services.py", "button.py", "switch.py")
    )
    for key in EXPECTED:
        assert f'translation_key="{key}"' in source
    assert "translation_domain=DOMAIN" in source
    assert "ServiceValidationError" in source
    assert 'HomeAssistantError("No matching loaded' not in source
    assert 'HomeAssistantError(f"BTicino' not in source
