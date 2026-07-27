# Ecosystem documentation

This section defines how BTDoor Platform can evolve from the current BTDoor Security+ video-door-entry integration into a unified BTicino and Netatmo platform.

## Truth model

Every ecosystem document separates three layers:

1. **Implemented now** — behavior present in `custom_components/btdoor_security_plus`.
2. **Architecture contract** — stable abstractions that future adapters must follow.
3. **Roadmap** — planned functionality that must not be interpreted as current support.

The current runtime is focused on BTDoor Security+ access, SIP/voice, media, diagnostics, services, events and Home Assistant entities. Broader BTicino, Netatmo, MyHOME, climate, energy and security coverage remains planned unless explicitly marked implemented.

## Canonical documents

- [Ecosystem support matrix](SUPPORT_MATRIX.md)
- [Capability model](CAPABILITY_MODEL.md)
- [Adapter contract](ADAPTER_CONTRACT.md)
- [Discovery and identity](DISCOVERY_AND_IDENTITY.md)
- [BTicino](BTICINO.md)
- [Netatmo](NETATMO.md)
- [Video door entry](VIDEO_DOOR_ENTRY.md)
- [MyHOME](MYHOME.md)
- [Home + Control](HOME_CONTROL.md)
- [Home + Security](HOME_SECURITY.md)
- [Living Now with Netatmo](LIVING_NOW.md)
- [Livinglight with Netatmo](LIVINGLIGHT.md)
- [MatixGO with Netatmo](MATIXGO.md)
- [BTDIN](BTDIN.md)
- [Smarther](SMARTHER.md)

## Related decisions

- [ADR-0036 — Unified ecosystem model](../adr/ADR-0036-unified-ecosystem-model.md)
- [ADR-0048 — Ecosystem documentation contract](../adr/ADR-0048-ecosystem-documentation-contract.md)
- [ADR-0049 — Capability adapter boundary](../adr/ADR-0049-capability-adapter-boundary.md)
- [Roadmap 2.x](../roadmap/ROADMAP_2X.md)
