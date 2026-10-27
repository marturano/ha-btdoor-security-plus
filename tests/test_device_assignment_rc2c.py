from pathlib import Path


def test_last_call_summary_is_attached_to_calls_device():
    sensor = (
        Path(__file__).parents[1] / "custom_components" / "btdoor_security_plus" / "sensor.py"
    ).read_text()
    start = sensor.index("class BTDoorLastCallSummarySensor")
    end = sensor.index("class BTDoorLastMediaCloseReasonSensor", start)
    block = sensor[start:end]
    assert "_device_kind = DeviceKind.DIALOG" in block
    assert "_device_kind = DeviceKind.MEDIA" not in block
    assert 'f"{entry.unique_id}_last_call_summary"' in block
