# ADR-0082: QS-14 Core Runtime and Event Bus Coverage

## Status

Accepted.

## Context

After QS-13, measured integration coverage was 87.63%. Core runtime orchestration and the persistent Runtime Event Bus still contained uncovered lifecycle, rollback, eviction and subscription branches.

## Decision

Add behavioural tests against the real core runtime, dispatcher and Event Bus modules using deterministic stores and subsystem hooks. Preserve runtime behavior and use only completed pytest-cov evidence for Quality Scale decisions.

## Consequences

Measured integration coverage rises to 88.42%. `core/runtime.py` reaches approximately 96% and the Event Bus implementation is fully exercised. Silver remains blocked by the strict greater-than-95% threshold.
