"""Central sanitization policy for exported BTDoor Security+ diagnostics."""

from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import Any

from .support_debug import redact_support_text


class ExportPolicy(StrEnum):
    """Supported export sanitization profiles."""

    STANDARD = "standard"
    DEVELOPER = "developer"


_SECRET_KEYS = frozenset(
    {
        "password",
        "sip_password",
        "auth_token",
        "access_token",
        "refresh_token",
        "authorization",
        "proxy-authorization",
        "nonce",
        "response",
        "client_key",
        "private_key",
        "csr",
        "cookie",
        "set-cookie",
        "certificate",
        "client_certificate",
        "client_cert_path",
        "client_key_path",
        "ca_chain_path",
    }
)
_HASHED_IDENTIFIER_KEYS = frozenset(
    {
        "entry_id",
        "config_entry_id",
        "device_id",
        "via_device_id",
        "unique_id",
        "entity_id",
        "plant_id",
        "id_device",
        "call_id",
        "branch",
        "tag",
        "instance",
    }
)


def _digest(value: str) -> str:
    """Return a stable, short, non-reversible identifier."""
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:12]


def sanitize_identifier(value: Any) -> str:
    """Hash a persistent identifier while preserving correlation in one bundle."""
    return f"[HASH:{_digest(str(value).strip(chr(34)))}]"


def sanitize_gateway_id(value: Any) -> str:
    """Partially mask a gateway identifier without exposing the full value."""
    text = str(value)
    if not text:
        return ""
    visible = min(3, len(text))
    return f"{text[:visible]}{'*' * max(4, len(text) - visible)}"


def sanitize_export_data(
    value: Any,
    key: str | None = None,
    *,
    policy: ExportPolicy = ExportPolicy.STANDARD,
) -> Any:
    """Return a JSON-safe recursively sanitized copy of exported data.

    Both profiles always remove credentials and cryptographic material. The
    standard profile also anonymizes persistent Home Assistant and gateway
    identifiers. The developer profile is reserved for future developer-only
    exports; it keeps gateway identifiers masked and hashes platform IDs so
    diagnostic records remain correlatable without disclosing raw values.
    """
    normalized_key = key.lower() if key else None

    if normalized_key in _SECRET_KEYS:
        return "[REDACTED]"

    if isinstance(value, dict):
        return {
            str(item_key): sanitize_export_data(
                item_value,
                str(item_key),
                policy=policy,
            )
            for item_key, item_value in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [sanitize_export_data(item, key, policy=policy) for item in value]
    if isinstance(value, bytes):
        return redact_support_text(value.decode("utf-8", "replace"))

    if normalized_key == "gateway_id" and value is not None:
        return sanitize_gateway_id(value)
    if normalized_key in _HASHED_IDENTIFIER_KEYS and value is not None:
        return sanitize_identifier(value)

    if isinstance(value, str):
        return redact_support_text(value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return redact_support_text(str(value))
