from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_rc7_version_and_platform():
    const = (ROOT / "custom_components/btdoor_security_plus/const.py").read_text()
    manifest = json.loads(
        (ROOT / "custom_components/btdoor_security_plus/manifest.json").read_text()
    )
    version = manifest["version"]
    assert version.startswith("1.1.0-rc.")
    assert f'INTEGRATION_VERSION = "{version}"' in const

def test_voice_bridge_uses_dedicated_device():
    switch = (ROOT / "custom_components/btdoor_security_plus/switch.py").read_text()
    factory = (ROOT / "custom_components/btdoor_security_plus/device_model/factory.py").read_text()
    assert "_device_kind = DeviceKind.VOICE_BRIDGE" in switch
    assert 'VOICE_BRIDGE = "voice_bridge"' in factory
    assert "kind not in {DeviceKind.GATEWAY, DeviceKind.VOICE_BRIDGE}" in factory

def test_active_dashboard_has_no_retired_cover():
    paths = [ROOT / "custom_components/btdoor_security_plus/ux/dashboard_builder.py", *list((ROOT / "dashboards").rglob("*.yaml"))]
    for path in paths:
        assert "cover.btdoor_template_gate" not in path.read_text()

def test_release_workflow_uses_current_notes_location():
    workflow = (ROOT / ".github/workflows/release.yml").read_text()
    assert 'docs/release/${version}.md' in workflow
    assert 'body_path: docs/release/${{ steps.version.outputs.value }}.md' in workflow
