# QS-3 Sensor Coverage Report

## Scope

QS-3 concentrated on `custom_components/btdoor_security_plus/sensor.py`, the largest uncovered Home Assistant entity platform after QS-2.

## Measured result

- Previous total integration coverage: **40.59%**
- Current total integration coverage: **53.24%**
- Net increase: **12.65 percentage points**
- `sensor.py`: **704/713 statements covered (98.74%)**
- Test suite: **249 passing tests**

## Behavioural evidence

`tests/test_quality_scale_qs3_sensor_platform.py` exercises:

- entity setup with developer mode enabled and disabled;
- all public sensor classes and their state/attribute projections;
- listener registration for SIP, runtime event bus, and call journal entities;
- API-backed and compatibility fallback paths;
- connection-quality thresholds;
- absent SDP/media values;
- absent API and journal states;
- developer runtime inspector states.

## Quality Scale decision

Silver remains blocked because total measured integration coverage is below the required threshold above 95%. No tier promotion is declared.

## Next priority

1. `services.py`
2. `cloud.py`
3. `__init__.py`
4. `sip_client.py`
