# ADR-0060 — Runtime and Release Certification

**Status:** Accepted

## Decision

Introduce a four-class certification model: repository, local runtime, Home Assistant target runtime and publication lifecycle. Evidence must identify its execution environment. Local validation cannot silently close target-runtime or HACS blockers.

## Consequences

The release decision remains BLOCKED until target evidence exists, even when the certification framework itself passes.
