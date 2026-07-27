# Smarther and Smarther2

Climate control integrated through canonical thermostat and zone capabilities.

## Status

| Field | Value |
|---|---|
| Current maturity | **Foundation** |
| Roadmap | **2.3** |
| Runtime statement | No dedicated runtime adapter for this product family is included in `1.1.0-rc.15`; this document defines the target contract and must not be read as a support claim. |

## Capability scope

| Area | Contract |
|---|---|
| Climate | Mode, target temperature and current temperature |
| Scheduling | Program and temporary override |
| Profiles | Away, antifreeze and boost |
| Optimization | Open-window and energy-aware control |

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
