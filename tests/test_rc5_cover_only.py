from pathlib import Path
import json

ROOT = Path(__file__).parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"


def test_voice_friendly_button_is_packaged():
    source = (COMPONENT / "button.py").read_text(encoding="utf-8")
    assert "BTDoorGateOpenButton" in source
    assert "async_press" in source
    assert "_open_gate_button" in source
    assert "SERVICE_OPEN_GATE" in source


def test_cover_platform_is_not_forwarded():
    const = (COMPONENT / "const.py").read_text(encoding="utf-8")
    assert '"cover"' not in const.split("PLATFORMS =", 1)[1].split("\n", 1)[0]


def test_gate_translation_exists_for_every_language():
    strings = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
    assert strings["entity"]["button"]["open_gate"]["name"]
    for path in (COMPONENT / "translations").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["entity"]["button"]["open_gate"]["name"], path.name


def test_version_is_consistent():
    manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))
    const = (COMPONENT / "const.py").read_text(encoding="utf-8")
    assert manifest["version"] == "1.1.0-rc.15"
    assert 'INTEGRATION_VERSION = "1.1.0-rc.15"' in const


def test_legacy_gate_switch_is_replaced_by_optional_voice_bridge():
    const = (COMPONENT / "const.py").read_text(encoding="utf-8")
    switch_source = (COMPONENT / "switch.py").read_text(encoding="utf-8")
    assert '"switch"' in const.split("PLATFORMS =", 1)[1].split("\n", 1)[0]
    assert "open_gate_voice_bridge" in switch_source
    assert "CONF_QUICK_VOICE_GATE" in switch_source
    services = (COMPONENT / "services.yaml").read_text(encoding="utf-8")
    assert "domain: button" in services
    assert "domain: switch" not in services


def test_legacy_switch_registry_cleanup_is_present():
    source = (COMPONENT / "__init__.py").read_text(encoding="utf-8")
    assert "_async_remove_legacy_gate_entities" in source
    assert 'registry.async_get_entity_id(platform, DOMAIN, unique_id)' in source
    assert "registry.async_remove(entity_id)" in source
