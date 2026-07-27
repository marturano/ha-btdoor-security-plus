# ADR-0063: Repository Production Audit

- Status: Accepted
- Date: 2026-07-22

## Decision

Adopt an automated, reproducible repository production audit as Phase 7A and include it in the governance orchestrator.

## Rationale

Release certification must distinguish repository hygiene from runtime evidence. The audit therefore verifies production-facing repository controls while explicitly refusing to grant publication approval.

## Consequences

A repository can pass Phase 7A and still remain blocked for Final release. Target validation and certification retain authority over release approval.
