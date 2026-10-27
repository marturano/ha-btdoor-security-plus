"""Regression tests for the centralized export sanitizer."""

from custom_components.btdoor_security_plus.support_sanitizer import (
    sanitize_export_data,
    sanitize_gateway_id,
    sanitize_identifier,
)


def test_persistent_identifiers_are_anonymized_recursively() -> None:
    payload = {
        "entry_id": "entry-123",
        "nested": {
            "config_entry_id": "entry-123",
            "device_id": "device-456",
            "gateway_id": "2621300",
            "authenticated": True,
        },
    }

    result = sanitize_export_data(payload)

    assert result["entry_id"] == sanitize_identifier("entry-123")
    assert result["nested"]["config_entry_id"] == sanitize_identifier("entry-123")
    assert result["nested"]["device_id"] == sanitize_identifier("device-456")
    assert result["nested"]["gateway_id"] == "262****"
    assert result["nested"]["authenticated"] is True


def test_secrets_are_never_exported() -> None:
    result = sanitize_export_data(
        {
            "password": "secret",
            "auth_token": "token",
            "private_key": "key",
            "certificate": "certificate-data",
        }
    )

    assert set(result.values()) == {"[REDACTED]"}


def test_identifier_hash_is_stable_and_non_reversible() -> None:
    first = sanitize_identifier("same-value")
    second = sanitize_identifier("same-value")

    assert first == second
    assert "same-value" not in first
    assert first.startswith("[HASH:")


def test_short_gateway_id_is_still_masked() -> None:
    assert sanitize_gateway_id("12") == "12****"
