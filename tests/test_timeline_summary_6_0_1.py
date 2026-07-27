"""Regression tests for SIP timeline classification in 6.0.1."""

from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "btdoor_security_plus"
    / "sip_timeline.py"
)
SPEC = importlib.util.spec_from_file_location("btdoor_sip_timeline", MODULE)
assert SPEC and SPEC.loader
sip_timeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sip_timeline)
classify_timeline_event = sip_timeline.classify_timeline_event


def test_classifies_runtime_sip_timeline_schema() -> None:
    cases = {
        "INVITE sip:user@example.invalid SIP/2.0": "INVITE",
        "CANCEL sip:user@example.invalid SIP/2.0": "CANCEL",
        "MESSAGE sip:server@example.invalid SIP/2.0": "MESSAGE",
        "REGISTER sip:example.invalid SIP/2.0": "REGISTER",
        "SIP/2.0 100 Trying": "1xx",
        "SIP/2.0 180 Ringing": "1xx",
        "SIP/2.0 200 Ok": "2xx",
        "SIP/2.0 302 Moved Temporarily": "3xx",
        "SIP/2.0 401 Unauthorized": "4xx",
        "SIP/2.0 407 Proxy Authentication Required": "4xx",
        "SIP/2.0 500 Server Internal Error": "5xx",
        "SIP/2.0 603 Decline": "6xx",
        "not a SIP frame": "unknown",
    }
    for line, expected in cases.items():
        assert classify_timeline_event({"line": line}) == expected


def test_preserves_explicit_event_type() -> None:
    assert classify_timeline_event({"event": "invite"}) == "invite"
    assert classify_timeline_event({"type": "bye"}) == "bye"


def test_uses_cseq_when_line_is_missing() -> None:
    assert classify_timeline_event({"cseq": "7 OPTIONS"}) == "OPTIONS"


def test_rejects_unknown_cseq_tokens() -> None:
    assert classify_timeline_event({"cseq": "7 SOMETHING"}) == "unknown"
