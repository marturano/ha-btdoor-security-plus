# ADR-0017 — Home Assistant observability entities

## Status
Accepted for 4.0.0-alpha.30.

## Decision
Expose stable runtime and persisted media information through native Home Assistant sensor and binary sensor entities. Entity state remains compact and automation-friendly, while structured technical details are retained as attributes.

The runtime health entity is intentionally synchronous and based only on live local facts (SIP registration, last error and media failure). It does not perform cloud requests from entity properties.

## Consequences
- Lovelace and automations no longer depend on Support Bundle inspection.
- Persisted call information remains visible after the dialog has terminated or Home Assistant has restarted.
- The entities can be selectively exposed to Alexa and Google Assistant through the standard Home Assistant exposure controls.
- Cloud connectivity is not represented by a misleading always-on entity; a dedicated cloud runtime entity will be added only when continuous cloud state exists.
