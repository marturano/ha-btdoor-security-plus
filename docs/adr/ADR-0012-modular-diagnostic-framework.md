# ADR-0012: Modular Diagnostic Framework

- Status: Accepted
- Version: 4.0.0-alpha.25

## Decision

BTDoor Security+ uses independent diagnostic providers implementing a common asynchronous contract. A diagnostic engine collects providers in isolation, a weighted health engine aggregates their normalized results, and the Support Bundle exports one JSON document per provider.

## Consequences

- A provider failure cannot suppress unrelated diagnostics.
- New engines such as RTP, SRTP, Netatmo or AI can contribute diagnostics without changing the orchestrator.
- Health scoring is weighted and non-cascading.
- Support Bundle schema 3 adds `diagnostics/providers/` while preserving legacy files.
