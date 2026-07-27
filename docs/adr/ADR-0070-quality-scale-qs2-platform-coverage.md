# ADR-0070 — Quality Scale QS-2 Platform Coverage

## Status
Accepted

## Context
The QS-1 baseline measured 35.54% integration coverage. Home Assistant entity platform modules were largely unexecuted in the repository test environment because Home Assistant is not installed there.

## Decision
Add behavioural contract tests that load the real integration platform modules with minimal Home Assistant API stubs. The tests exercise entity construction, visibility filtering, state and attribute mapping, service dispatch, error propagation, developer actions, event filtering, and diagnostics serialization.

The stubs model only the external Home Assistant interfaces needed by the tested code. Assertions remain focused on the integration's real behaviour; source-text assertions do not count as coverage evidence.

## Consequences
- Overall measured coverage rises from 35.54% to 40.59%.
- `binary_sensor.py`, `button.py`, `event.py`, `switch.py`, `entity.py`, `diagnostics.py`, and device-model paths now have executable evidence.
- Silver remains blocked by the greater-than-95% coverage requirement.
- The next highest-impact work is `sensor.py`, followed by `services.py`, `cloud.py`, `__init__.py`, and `sip_client.py`.
