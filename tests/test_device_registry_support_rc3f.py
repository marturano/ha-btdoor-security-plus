"""Regression checks for rc.3f device registry support exports."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_support_bundle_contains_registry_and_translation_reports() -> None:
    source = (ROOT / "custom_components/btdoor_security_plus/developer.py").read_text()
    assert '"registry/devices.json"' in source
    assert '"translations/report.json"' in source
    assert "device_registry_report(self.hass, self.entry)" in source


def test_registry_migration_preserves_user_names() -> None:
    source = (ROOT / "custom_components/btdoor_security_plus/device_model/manager.py").read_text()
    assert "device.name_by_user is None" in source
    assert "registry.async_update_device(device.id, **updates)" in source


def test_manifest_version() -> None:
    import json
    data = json.loads((ROOT / "custom_components/btdoor_security_plus/manifest.json").read_text())
    assert data["version"] == "6.0.1"
