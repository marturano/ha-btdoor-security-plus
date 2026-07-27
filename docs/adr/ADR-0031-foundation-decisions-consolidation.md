# ADR-0031 — Consolidated 1.0 Foundation decisions

- **Status:** Accepted
- **Canonical milestone:** 1.0 Foundation

## Context

The integration was developed continuously under several provisional version labels. ADR-0007 through ADR-0023 recorded valid decisions, but their release metadata no longer matched the canonical 1.0/1.1 product history.

## Decision

The original ADRs are retained unchanged under `adr/foundation/` as engineering evidence. Their still-valid decisions are consolidated here and in the normative architecture:

- the public domain is `btdoor_security_plus`;
- blocking work is kept off Home Assistant's event loop;
- Support Bundles are sanitized, private and reproducibly named;
- certificate migration and health providers fail independently;
- diagnostics use modular providers and retained normalized snapshots;
- SIP callers, dialogs, media sessions and events are normalized before entity consumption;
- logical devices and entity identities remain stable across upgrades;
- the Call Journal is event-driven;
- user documentation is localized while English engineering documents remain normative.

## Consequences

Archived ADR numbers remain searchable and must not be rewritten. New design changes receive new ADRs. Active documents use only the canonical 1.0 Foundation and 1.1 Core Stable terminology.
