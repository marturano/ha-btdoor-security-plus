# ADR-0015 — Normalized SIP caller identity

## Status
Accepted for 4.0.0-alpha.28.

## Context
The `Ultimo chiamante` entity exposed the complete SIP `From` header, including angle brackets and the transient dialog tag. This was technically correct but unsuitable as a Home Assistant entity state.

## Decision
Parse SIP party headers once in a shared runtime utility. The entity state uses the display name when present, otherwise the SIP user. URI, domain, tag, original header, call ID and call state remain available as entity attributes. Persisted alpha.27 raw values are migrated when restored.

## Consequences
Dashboards expose a stable readable value such as `c300x`; diagnostics retain protocol detail; parsing is reusable by future recipient, contact and address-book features.
