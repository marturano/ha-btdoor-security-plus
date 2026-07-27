# ADR-0079: QS-11 Adapter, Runtime API and Diagnostics Coverage

## Status

Accepted.

## Context

The Quality Scale test-coverage rule remained the sole Silver blocker after QS-10. Adapter foundations and runtime-state APIs were either uncovered or partially covered, despite being stable contracts consumed by entities, diagnostics and services.

## Decision

Add behavioural tests that execute the abstract adapter defaults, runtime snapshot construction, error-state scoring, support-bundle delegation, diagnostic result normalization and bundle path generation. Preserve the measured-coverage gate and do not promote Silver below the strict greater-than-95-percent threshold.

## Consequences

The adapter base and runtime-state provider/API now have complete executable coverage. Overall integration coverage rises to 80.49%. Cloud and SIP dispatch remain the dominant uncovered areas and become the next priority.
