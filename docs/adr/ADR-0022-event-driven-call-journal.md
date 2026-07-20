# ADR-0022: Event-driven persistent Call Journal

Status: Accepted for 5.1.0-beta.1.

## Decision

Build the call journal only from normalized Runtime Event Bus events. Persist at most 250 completed call records per config entry. Runtime engines and entity implementations must not write journal records directly.

## Consequences

The same history can feed Home Assistant entities, dashboards, Support Bundles, statistics and future AI diagnostics without duplicating call reconstruction logic.
