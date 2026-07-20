"""Regression tests for normalized caller identity."""
from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / "custom_components" / "btdoor_security_plus" / "sip_identity.py"
spec = importlib.util.spec_from_file_location("sip_identity_alpha28", MODULE)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)
parse_sip_identity = module.parse_sip_identity


def test_parse_bticino_from_header() -> None:
    identity = parse_sip_identity("<sip:c300x@2621300.bs.iotleg.com>;tag=m8qOjgmms")
    assert identity is not None
    assert identity.label == "c300x"
    assert identity.uri == "sip:c300x@2621300.bs.iotleg.com"
    assert identity.user == "c300x"
    assert identity.domain == "2621300.bs.iotleg.com"
    assert identity.tag == "m8qOjgmms"


def test_display_name_is_preferred() -> None:
    identity = parse_sip_identity('"Ingresso principale" <sip:c300x@example.net>;tag=abc')
    assert identity is not None
    assert identity.label == "Ingresso principale"
    assert identity.user == "c300x"


def test_bare_uri_and_empty_values() -> None:
    identity = parse_sip_identity("sip:door@example.net")
    assert identity is not None
    assert identity.label == "door"
    assert parse_sip_identity(None) is None
    assert parse_sip_identity("  ") is None
