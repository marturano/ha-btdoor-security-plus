"""Regression tests for support bundle sanitization."""

from __future__ import annotations

import json

from custom_components.btdoor_security_plus.support_models import (
    json_dumps,
    sanitize_jsonl,
    sanitize_support_data,
    structure_dialog_headers,
)


def test_problematic_sip_headers_remain_valid_json() -> None:
    headers = {
        "from": '<sip:c300x@example.invalid>;tag="quoted-tag"',
        "to": "<sip:client@example.invalid>",
        "contact": '<sip:c300x@127.0.0.1:45438;transport=tcp>;+sip.instance="<urn:uuid:f99a44d1-a257-4232-ad48-8a68c575cd29>"',
    }
    payload = structure_dialog_headers(headers)
    encoded = json_dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["from"]["tag"].startswith("[HASH:")
    assert decoded["contact"]["instance"].startswith("[HASH:")


def test_recursive_sanitizer_never_serializes_before_redaction() -> None:
    source = {"header": 'value "with quotes";tag=abc', "nested": ["192.168.1.50"]}
    encoded = json_dumps(sanitize_support_data(source))
    assert json.loads(encoded)
    assert "192.168.1.50" not in encoded


def test_jsonl_output_is_valid_per_line() -> None:
    source = (
        json.dumps({"data": {"contact": '<sip:x@127.0.0.1>;+sip.instance="<urn:uuid:test>"'}})
        + "\n"
    )
    result = sanitize_jsonl(source)
    for line in result.splitlines():
        json.loads(line)
