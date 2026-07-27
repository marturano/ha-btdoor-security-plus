from pathlib import Path
import json

ROOT = Path(__file__).parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"

def test_rc6_gate_button_and_platform():
    source = (COMPONENT / "button.py").read_text()
    const = (COMPONENT / "const.py").read_text()
    assert "class BTDoorGateOpenButton" in source
    assert "SERVICE_OPEN_GATE" in source
    assert "_open_gate_button" in source
    platforms = const.split("PLATFORMS =", 1)[1].split("\n", 1)[0]
    assert '"button"' in platforms
    assert '"cover"' not in platforms

def test_quick_voice_option_and_warning():
    flow = (COMPONENT / "config_flow.py").read_text()
    assert "CONF_QUICK_VOICE_GATE" in flow
    assert "async_step_confirm_quick_voice" in flow
    it = json.loads((COMPONENT / "translations" / "it.json").read_text())
    assert it["options"]["step"]["confirm_quick_voice"]["description"]

def test_retired_gate_entities_are_cleaned():
    source = (COMPONENT / "__init__.py").read_text()
    assert '("cover", f"{entry.unique_id}_gate_cover")' in source
    assert '("switch", f"{entry.unique_id}_open_gate_switch")' in source

def test_support_sanitizer_hashes_registry_ids():
    source = (COMPONENT / "support_sanitizer.py").read_text()
    for key in ("via_device_id", "unique_id", "entity_id"):
        assert f'"{key}"' in source
