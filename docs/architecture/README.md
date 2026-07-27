# Architecture documentation

This directory is the canonical architecture source for BTDoor Security+.
Architecture documents describe the implementation that exists in the repository and clearly label future capabilities.

## System and runtime

- [System architecture](SYSTEM_ARCHITECTURE.md)
- [Core runtime](CORE_RUNTIME.md)
- [Lifecycle and isolation](LIFECYCLE_AND_ISOLATION.md)
- [Configuration entry model](CONFIG_ENTRY_MODEL.md)
- [Data flow](DATA_FLOW.md)
- [Module boundaries](MODULE_BOUNDARIES.md)

## Domain models

- [Device model](DEVICE_MODEL.md)
- [Entity model](ENTITY_MODEL.md)
- [Service model](SERVICE_MODEL.md)
- [Event model](EVENT_MODEL.md)
- [Device and entity compatibility entry point](DEVICE_ENTITY_MODEL.md)

## Pipelines

- [Event bus](EVENT_BUS.md)
- [Media pipeline](MEDIA_PIPELINE.md)
- [Voice pipeline](VOICE_PIPELINE.md)
- [Notification pipeline](NOTIFICATION_PIPELINE.md)
- [AI pipeline](AI_PIPELINE.md)
- [Timeline engine](TIMELINE_ENGINE.md)

## Operational architecture

- [Diagnostics and support](DIAGNOSTICS_AND_SUPPORT.md)
- [Health score](HEALTH_SCORE.md)
- [Gate and voice bridge](GATE_AND_VOICE_BRIDGE.md)

## Normative rules

1. Runtime behavior is authoritative only when supported by code or tests.
2. Planned components must be marked **Planned** and linked to the roadmap.
3. Every architecture document must identify implementation modules.
4. Entry-local ownership is required for multi-entry safety.
5. Secrets, certificate material and raw personal data must not enter diagnostics or events.
