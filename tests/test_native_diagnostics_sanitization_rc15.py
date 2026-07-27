"""Regression checks for native Home Assistant diagnostics sanitization."""

from pathlib import Path

from custom_components.btdoor_security_plus.support_models import sanitize_support_data

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS = ROOT / "custom_components" / "btdoor_security_plus" / "diagnostics.py"


def test_native_diagnostics_use_central_sanitization_policy() -> None:
    source = DIAGNOSTICS.read_text(encoding="utf-8")
    assert "sanitize_support_data" in source
    assert "async_redact_data" not in source


def test_native_diagnostics_payload_masks_sensitive_runtime_data() -> None:
    payload = sanitize_support_data(
        {
            "entry": {
                "password": "secret-password",
                "sip_password": "secret-sip-password",
                "client_key_path": "/config/private/client-key.pem",
                "gateway_id": "001122334455",
                "entry_id": "entry-123",
            },
            "runtime": {
                "target_uri": "sip:user@192.168.1.42",
                "last_call_id": "private-call-id@example.invalid",
                "last_sdp_offer": "c=IN IP4 10.0.0.55",
            },
        }
    )

    encoded = repr(payload)
    assert "secret-password" not in encoded
    assert "secret-sip-password" not in encoded
    assert "/config/private/client-key.pem" not in encoded
    assert "001122334455" not in encoded
    assert "entry-123" not in encoded
    assert "192.168.1.42" not in encoded
    assert "10.0.0.55" not in encoded
    assert "private-call-id@example.invalid" not in encoded
    assert "[REDACTED]" in encoded
    assert "xxx.xxx" in encoded
    assert "[HASH:" in encoded
