"""Regression tests for beta.4.1 runtime event producer wiring."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"


def test_sip_dispatcher_emits_invite_received() -> None:
    source = (COMPONENT / "sip_client.py").read_text(encoding="utf-8")
    assert 'self._notify(\n                    "invite_received"' in source


def test_mapper_handles_actual_media_notifications() -> None:
    source = (COMPONENT / "event_bus" / "mapper.py").read_text(encoding="utf-8")
    assert '"media_session_prepared"' in source
    assert '"media_session_failed"' in source
    assert '"media_session_closed"' in source


def test_setup_synchronizes_initial_runtime_state() -> None:
    source = (COMPONENT / "__init__.py").read_text(encoding="utf-8")
    assert '"synchronized": True' in source
    assert "RuntimeEventType.SIP_REGISTERED" in source
    assert "RuntimeEventType.CLOUD_CONNECTED" in source
