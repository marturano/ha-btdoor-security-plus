# ADR-0066: Quality Scale as a governed workflow

- **Status:** Accepted
- **Date:** 2026-07-22

## Decision

The Home Assistant Integration Quality Scale becomes a mandatory phase-start, phase-end and release gate. The project maintains a release minimum tier and a desired evolution tier. Assessments generate remediation work; only deterministic safe changes may be automated, and no rule may be promoted without evidence.

## Consequences

Release Readiness is blocked below the configured minimum. Gaps to the desired tier remain visible in roadmap, health, validation and handoff. Custom-integration results remain self-assessments and must not be represented as an official Home Assistant Core grade.
