# ADR-0056 — Voice Assistant Exposure Boundary

Status: Accepted

## Context

Alexa, Alexa+ and Google Assistant have independent discovery and secure-action policies.

## Decision

BTDoor Security+ exposes Home Assistant entities only. Home Assistant Cloud or assistant integrations control external exposure. The optional switch is a compatibility bridge, not a direct vendor API.

## Consequences

Assistant compatibility requires real-account/device validation and must not be inferred from entity creation alone.
