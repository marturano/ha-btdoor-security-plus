# ADR-0059 — Quality and Release Intelligence

- **Status:** Accepted
- **Date:** 2026-07-22

## Context

Gate decisions existed, but their evidence, risks and release consequences were distributed across narrative documents. Aggregate health scores could not explain a Final approval decision by themselves.

## Decision

Maintain structured canonical registries for evidence, risks, technical debt and decision traceability. Generate a machine-readable and human-readable release decision from those registries. Tooling validity and release approval are separate outcomes: the automation can pass while the release remains blocked.

## Consequences

- Every formal gate must reference evidence IDs.
- Open blocking evidence prevents approval.
- Open CRITICAL or HIGH risks prevent approval unless a formal exception is recorded.
- Technical debt cannot substitute for unresolved defects or failed gates.
- Release decisions are reproducible and auditable.
