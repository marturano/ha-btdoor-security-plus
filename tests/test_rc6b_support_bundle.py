from pathlib import Path

ROOT = Path(__file__).parents[1]
DOMAIN = ROOT / "custom_components" / "btdoor_security_plus"


def test_support_bundle_contains_entity_registry_snapshot():
    source = (DOMAIN / "developer.py").read_text()
    assert "def _entity_registry_report" in source
    assert "async_entries_for_config_entry" in source
    assert '"registry/entities.json"' in source
    assert '"translation_key"' in source
    assert '"disabled_by"' in source
    assert '"hidden_by"' in source


def test_voice_bridge_switch_is_enabled_by_default_when_created():
    source = (DOMAIN / "switch.py").read_text()
    assert "BTDoorGateVoiceBridgeSwitch" in source
    assert "_attr_entity_registry_enabled_default = False" not in source
