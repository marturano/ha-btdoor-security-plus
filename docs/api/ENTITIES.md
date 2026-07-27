# Entity Contract

## Status

Implemented entity platforms are defined by the integration package. Entity presence depends on configuration, runtime capability and options; a roadmap entry does not imply that an entity exists.

## Stable identity

- Every entity must have a stable `unique_id` derived from the owning config entry/device identity and entity role.
- Entities belong to exactly one Home Assistant device and one config entry runtime.
- Renaming an entity in Home Assistant must not change its `unique_id`.
- Display names and states use translation keys rather than hard-coded user-facing text.

## Current platform surface

| Platform | Purpose | Exposure guidance |
|---|---|---|
| `button` | Native gate-open action | Preferred Home Assistant control surface; expose to voice assistants only after reviewing their security model. |
| `switch` | Optional voice bridge for assistants that discover switches more reliably | Compatibility bridge, not a physical-state claim; must return to a safe/off state after activation. |
| `binary_sensor` | Runtime connectivity/call conditions where implemented | Read-only; generally safe to expose selectively. |
| `sensor` | Counters, diagnostics and runtime metrics | Avoid exposing sensitive diagnostics or identifiers. |
| `event` | Door-entry/runtime event entity | Event payloads are transient and may contain contextual metadata. |

## Availability

An entity is unavailable when its owning config entry is not loaded or its runtime cannot provide valid state. Entity properties must read from memory and must not perform network I/O.

## Compatibility

Consumers must use domain semantics and documented attributes. Undocumented attributes are diagnostic implementation details and may change between release candidates.

## Related code

- `custom_components/btdoor_security_plus/entity.py`
- `custom_components/btdoor_security_plus/button.py`
- `custom_components/btdoor_security_plus/switch.py`
- `custom_components/btdoor_security_plus/sensor.py`
- `custom_components/btdoor_security_plus/binary_sensor.py`
- `custom_components/btdoor_security_plus/event.py`
