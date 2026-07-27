# Video door entry

Access, call, SIP, media and relay capabilities for BTicino-compatible door-entry systems.

## Status

| Field | Value |
|---|---|
| Current maturity | **Implemented / Foundation** |
| Roadmap | **1.x and 2.6** |
| Runtime statement | Current BTDoor Security+ runtime implements the documented access, SIP/voice foundation, media helpers, services, events and diagnostics. Generalized multi-model support remains a foundation item. |

## Capability scope

| Area | Contract |
|---|---|
| Access | Gate/door actions and command routing |
| Calls | Call state and normalized events |
| Voice | SIP identity and voice session foundation |
| Media | Snapshots, clips and timeline helpers |
| Diagnostics | Sanitized support bundle and health evidence |

## Home Assistant mapping principles

- Create entities only for capabilities verified on the device.
- Preserve unique IDs across room, name and transport changes.
- Use services for parameterized actions and events for stateless activity.
- Publish availability and diagnostic reason separately from functional state.
- Expose voice assistants only through security-appropriate Home Assistant entities and policies.

## Dependencies and acceptance

A runtime adapter requires a verified device/protocol matrix, sanitized diagnostics, config-entry isolation, translation coverage, migration tests and updates to [SUPPORT_MATRIX.md](SUPPORT_MATRIX.md).

## Related documentation

- [Capability model](CAPABILITY_MODEL.md)
- [Adapter contract](ADAPTER_CONTRACT.md)
- [Discovery and identity](DISCOVERY_AND_IDENTITY.md)
- [Roadmap 2.x](../roadmap/ROADMAP_2X.md)
