from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_rc3_names_and_options_are_present():
    factory = (ROOT / "custom_components/btdoor_security_plus/device_model/factory.py").read_text()
    names = (ROOT / "custom_components/btdoor_security_plus/device_model/names.py").read_text()
    for name in (
        "Cloud Status",
        "SIP Monitor",
        "Call Manager",
        "Multimedia Monitor",
        "Advanced Diagnostics",
    ):
        assert name in factory or name in names
    config = (ROOT / "custom_components/btdoor_security_plus/config_flow.py").read_text()
    for key in (
        "CONF_SHOW_CLOUD_STATUS",
        "CONF_SHOW_SIP_MONITOR",
        "CONF_SHOW_CALL_MONITOR",
        "CONF_SHOW_MEDIA_MONITOR",
        "CONF_SHOW_ADVANCED_DIAGNOSTICS",
    ):
        assert key in config


def test_every_visibility_option_has_description():
    import json

    data = json.loads(
        (ROOT / "custom_components/btdoor_security_plus/translations/it.json").read_text()
    )
    step = data["options"]["step"]["init"]
    for key in (
        "show_cloud_status",
        "show_sip_monitor",
        "show_call_monitor",
        "show_media_monitor",
        "show_advanced_diagnostics",
        "developer_mode",
        "debug_mode",
    ):
        assert step["data"].get(key)
        assert step["data_description"].get(key)
