from pathlib import Path
import json

ROOT = Path(__file__).parents[1]
DOMAIN = ROOT / "custom_components" / "btdoor_security_plus"


def test_version_and_platforms():
    manifest = json.loads((DOMAIN / "manifest.json").read_text())
    const = (DOMAIN / "const.py").read_text()
    version = manifest["version"]
    assert version.startswith("1.1.0-rc.")
    assert f'INTEGRATION_VERSION = "{version}"' in const
    assert '"switch"' in const


def test_voice_bridge_is_optional_and_stateless():
    source = (DOMAIN / "switch.py").read_text()
    assert "CONF_QUICK_VOICE_GATE" in source
    assert "BTDoorGateVoiceBridgeSwitch" in source
    assert '_attr_is_on = False' in source
    assert 'SERVICE_OPEN_GATE' in source
    assert 'voice_bridge_switch' in source


def test_assist_restart_issue_not_created_during_startup():
    source = (DOMAIN / "__init__.py").read_text()
    assert "CoreState.running" in source
    assert "sentences_changed" in source


def test_switch_translations_exist():
    for path in [DOMAIN / "strings.json", *sorted((DOMAIN / "translations").glob("*.json"))]:
        data = json.loads(path.read_text())
        assert data["entity"]["switch"]["open_gate_voice_bridge"]["name"]
