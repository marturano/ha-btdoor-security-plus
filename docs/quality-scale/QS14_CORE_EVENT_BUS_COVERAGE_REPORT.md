# QS-14 Core Runtime and Event Bus Coverage Report

## Result

Measured integration coverage increased from **87.63%** to **88.42%**.

- Covered statements: 4926 / 5571
- Missing statements: 645
- Silver threshold: above 95%
- Current tier: Bronze

## Implemented tests

Added `tests/test_quality_scale_qs14_core_event_bus.py` covering:

- persisted Runtime Event Bus loading with invalid-record tolerance;
- bounded history eviction and counter correction;
- global and typed listener subscription/removal;
- delayed persistence, compact history, metrics and empty-state behavior;
- core runtime ordered startup and reverse shutdown;
- idempotent startup, restart and diagnostics;
- startup rollback after partial failure;
- aggregated shutdown errors and invalid lifecycle transitions;
- typed dispatcher facade;
- lazy manager export resolution.

## Validation

- QS-14 tests: 6 PASS.
- Main behavioural suite: 297 PASS.
- Runtime Release Certification: PASS.
- Target Validation Pack: PASS.
- Quality Scale Engine and workflow: PASS.

Silver remains blocked because measured integration coverage does not yet exceed 95%.
