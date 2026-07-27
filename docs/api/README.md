# API Foundation

Status: **RC.15 Phase 5 — normative documentation for the current Home Assistant surface; future transports remain contract-only**.

The public API of BTDoor Security+ is the set of surfaces intentionally exposed through Home Assistant. Internal Python modules, dispatcher signals and implementation details are not public merely because they are importable.

## Current public surfaces

- [Entity contract](ENTITIES.md)
- [Action/service contract](SERVICES.md)
- [Event contract](EVENTS.md)
- [Error contract](ERRORS.md)
- [Versioning and compatibility](VERSIONING.md)
- [Security and authorization](SECURITY.md)
- [Voice assistant exposure](VOICE_ASSISTANTS.md)
- [Automation examples](AUTOMATION_EXAMPLES.md)

## Planned developer-platform surfaces

- [REST API](REST.md)
- [WebSocket API](WEBSOCKET.md)

REST and WebSocket are not implemented public endpoints in RC.15. Home Assistant's own APIs may expose entity state, action execution and event subscriptions, but that does not create a BTDoor-specific transport compatibility promise.

## Contract rules

1. Public names are documented before they are considered stable.
2. Additive fields are backward compatible unless explicitly marked otherwise.
3. Removal or semantic change requires deprecation, migration guidance and an ADR.
4. Physical security actions must remain explicitly targeted and auditable.
5. Alexa, Alexa+ and Google Assistant consume exposed Home Assistant entities; they do not call private integration internals.
