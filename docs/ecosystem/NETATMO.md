# Netatmo ecosystem

Cloud and local-capable products for security, climate, weather and environmental monitoring.

## Status

| Field | Value |
|---|---|
| Current maturity | **Foundation** |
| Roadmap | **2.3–2.5** |
| Runtime statement | No dedicated runtime adapter for this product family is included in `1.1.0-rc.15`; this document defines the target contract and must not be read as a support claim. |

## Capability scope

| Area | Contract |
|---|---|
| Security | Cameras, sirens, sensors and smoke/CO events |
| Climate | Thermostats, valves, zones and schedules |
| Environment | Weather, air quality, comfort and outdoor measurements |

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
