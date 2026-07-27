from pathlib import Path


def test_developer_mode_entities_are_packaged():
    text = Path("custom_components/btdoor_security_plus/sensor.py").read_text()
    for name in (
        "BTDoorDeveloperRuntimeInspectorSensor",
        "BTDoorDeveloperEventMonitorSensor",
        "BTDoorDeveloperEventMetricsSensor",
    ):
        assert name in text
    assert "bus.compact_history(20)" in text
    assert 'item.get("payload")' not in text


def test_runtime_inspector_serializes_supported_snapshot_api():
    text = Path("custom_components/btdoor_security_plus/sensor.py").read_text()
    assert "snapshot_data = snapshot.as_dict()" in text
    for nested in ("gateway", "cloud", "sip", "dialog", "media", "diagnostics"):
        assert f"snapshot.{nested}.as_dict()" not in text
