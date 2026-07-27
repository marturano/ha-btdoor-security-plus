# Phase 7C Target Validation Readiness

**Package:** `1.1.0-rc.15-phase7c-target-matrix-corrected`  
**Phase:** Phase 7C — Release Candidate Approval  
**Decision:** BLOCKED pending real target evidence

## Scope

This iteration prepares the existing Target Validation Pack for controlled execution on a real Home Assistant 2026.x, with 2026.7.x as the reference target instance. It does not add runtime features and does not claim target validation has been completed.

## Implemented

- Per-run generated field checklist.
- Machine-readable progress summary through the `status` command.
- Explicit mapping between validation domains and blocking evidence IDs.
- Primary-target enforcement for Home Assistant 2026.x, with 2026.7.x as the reference target.
- Safe evidence-path validation preventing absolute paths and traversal outside the run directory.
- Sanitized automatic collection that retains a host label instead of the full Home Assistant URL.
- Operator field checklist covering runtime, compatibility, HACS lifecycle, security and UX/accessibility.
- Evidence sanitization guidance.
- Regression tests for run generation, incomplete import rejection and unsafe evidence paths.

## Validation

The Target Validation Pack test module passes. Repository-wide gates must still be rerun for the exact package before delivery.

## Remaining blockers

- `EV-PERF-002` — measured runtime and performance evidence.
- `EV-COMP-001` — Home Assistant 2026.x, with 2026.7.x as the reference target lifecycle evidence.
- `EV-PUB-001` — HACS install, upgrade and rollback evidence.
- `EV-SEC-002` — target-runtime security evidence.
- `EV-UX-001` — interactive UX/accessibility evidence.
- `EV-HAQS-001` — final external Quality Scale evidence.
- CI evidence for Ruff, mypy, HACS Action and hassfest.

## Exit rule

The package is ready to collect evidence but Phase 7C remains active and blocked. A run may update certification only after every required check is validated, sanitized evidence is retained, operator attestation is complete and the immutable import succeeds.
