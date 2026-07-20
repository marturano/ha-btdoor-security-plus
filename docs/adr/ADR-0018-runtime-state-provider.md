# ADR-0018 — Stable Runtime State Provider

## Status
Accepted for 5.0.0-beta.1.

## Context
Home Assistant entities, support exports and future services were reading mutable SIP, dialog and media runtime objects directly. This duplicated normalization logic and coupled presentation code to engine internals.

## Decision
Introduce immutable state models and a single `RuntimeStateProvider` facade. The stable internal `BTDoorRuntimeAPI` exposes gateway, cloud, SIP, dialog, media and diagnostic snapshots. Existing entity unique IDs remain unchanged; the first observability entities now consume the facade while compatibility fallbacks remain available.

## Consequences
Runtime engines may be refactored without changing consumers. Support Bundle, device model, dashboard, services and AI diagnostics can converge on the same schema. Snapshot construction is synchronous and side-effect free; commands remain explicit asynchronous API methods.
