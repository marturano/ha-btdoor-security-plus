"""Static regression tests for the Beta.2 device model."""

from pathlib import Path

ROOT = Path(__file__).parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"


def test_device_model_defines_complete_hierarchy():
    source = (COMPONENT / "device_model" / "factory.py").read_text()
    for kind in ("GATEWAY", "CLOUD", "SIP", "DIALOG", "MEDIA", "DIAGNOSTICS"):
        assert f"{kind} =" in source
    assert 'info["via_device"] = root' in source
    assert "sip_client_{id_device}" in source


def test_entity_unique_ids_are_not_rewritten():
    for filename in ("sensor.py", "binary_sensor.py", "button.py", "event.py"):
        source = (COMPONENT / filename).read_text()
        assert "_device_kind" in source
    assert 'f"{entry.unique_id}_open_gate_button"' in (COMPONENT / "button.py").read_text()
    assert 'f"{entry.unique_id}_sip_registered"' in (COMPONENT / "binary_sensor.py").read_text()


def test_setup_registers_devices_before_platforms():
    source = (COMPONENT / "__init__.py").read_text()
    assert source.index("await async_register_devices(hass, entry)") < source.index(
        "await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)"
    )
