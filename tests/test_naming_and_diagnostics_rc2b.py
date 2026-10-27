from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_new_configuration_and_device_names_are_packaged():
    init = (ROOT / "custom_components/btdoor_security_plus/__init__.py").read_text()
    flow = (ROOT / "custom_components/btdoor_security_plus/config_flow.py").read_text()
    factory = (ROOT / "custom_components/btdoor_security_plus/device_model/factory.py").read_text()
    names = (ROOT / "custom_components/btdoor_security_plus/device_model/names.py").read_text()
    assert "Bticino DS+ Suite" in init
    assert "Bticino DS+ Suite" in flow
    for name in (
        "Cloud Status",
        "Advanced Diagnostics",
        "Call Manager",
        "Multimedia Monitor",
        "SIP Monitor",
    ):
        assert name in factory or name in names


def test_diagnostics_device_is_controlled_by_visibility_manager():
    manager = (ROOT / "custom_components/btdoor_security_plus/device_model/manager.py").read_text()
    visibility = (ROOT / "custom_components/btdoor_security_plus/visibility/manager.py").read_text()
    sensor = (ROOT / "custom_components/btdoor_security_plus/sensor.py").read_text()
    binary_sensor = (ROOT / "custom_components/btdoor_security_plus/binary_sensor.py").read_text()
    assert "registry.async_remove_device" in manager
    assert "entity_registry.async_remove" in manager
    assert "visibility.is_visible(kind)" in manager
    assert "developer_mode and bool" in " ".join(visibility.split())
    assert "visibility_for_entry(entry).filter_entities" in sensor
    assert "visibility_for_entry(entry).filter_entities" in binary_sensor
