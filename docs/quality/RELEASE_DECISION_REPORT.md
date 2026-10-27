# Release Decision Report

**Generated:** 2026-10-27
**Target:** 1.1.0 Final
**Decision:** **BLOCKED**

## Gate decisions

| Gate | Status | Blocking evidence |
|---|---|---|
| Definition of Ready Gate | PASS | None |
| Architecture Gate | PASS | None |
| Quality Gate | PASS | None |
| Security Gate | BLOCKED | EV-SEC-002 |
| Performance Gate | BLOCKED | EV-PERF-002 |
| Documentation Gate | BLOCKED | EV-UX-001 |
| Validation Gate | BLOCKED | EV-COMP-001 |
| Release Readiness Gate | PASS | None |
| Publication Gate | BLOCKED | EV-PUB-001 |
| Home Assistant Quality Scale Gate | BLOCKED | EV-HAQS-001 |

## Blocking evidence

- `EV-SEC-002`
- `EV-PERF-002`
- `EV-UX-001`
- `EV-COMP-001`
- `EV-PUB-001`
- `EV-HAQS-001`

## Critical and high open risks

- `RISK-001`
- `RISK-002`
- `RISK-003`
- `RISK-004`

## Decision rule

The Final release is approved only when every blocking evidence item is validated, no open CRITICAL or HIGH risk remains without an explicitly approved exception, Quality Scale is GOLD, and RG-001 through RG-004 pass for the exact package.

## Approval semantics

Release Readiness `PASS` confirms package-level readiness checks only; Final approval remains `BLOCKED` until the Release Decision Engine returns `APPROVED`.
