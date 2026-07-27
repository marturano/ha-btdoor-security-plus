# QS-2 Platform Coverage Report

## Outcome

| Metric | QS-1 baseline | QS-2 result | Change |
|---|---:|---:|---:|
| Test count | 240 | 245 | +5 |
| Coverage | 35.54% | 40.59% | +5.05 percentage points |
| Covered statements | 1980 | 2261 | +281 |
| Missing statements | 3591 | 3310 | -281 |

## Platform results

- `binary_sensor.py`: 89%
- `button.py`: 95%
- `event.py`: 92%
- `switch.py`: complete and omitted from the missing-lines table
- `device_model/factory.py`: 96%
- `diagnostics.py`: complete and omitted from the missing-lines table
- `entity.py`: complete and omitted from the missing-lines table

## Quality Scale decision

The measured evidence remains below the Silver requirement of greater than 95%. The achieved tier therefore remains Bronze. No rule or tier was promoted from documentation alone.

## Next priority

1. `sensor.py` — 713 statements currently uncovered.
2. `services.py` — 135 statements currently uncovered.
3. `cloud.py` — 361 statements currently uncovered.
4. `__init__.py` — 255 statements currently uncovered.
5. `sip_client.py` — 813 statements still uncovered.
