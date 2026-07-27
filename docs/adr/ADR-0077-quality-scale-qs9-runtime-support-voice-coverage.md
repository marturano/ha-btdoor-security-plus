# ADR-0077: QS-9 Runtime, Support and Voice Coverage

## Status

Accepted

## Decision

Add behavioural tests for runtime container defaults, support-debug redaction/rotation/clear operations, managed Assist sentence installation, and the native open-gate voice intent.

Coverage evidence must come from a completed pytest-cov run. The two certification tests that launch nested subprocess suites are validated separately to avoid environmental timeout without reducing test execution.

## Consequences

Measured integration coverage rises from 73.49% to 76.56%. Runtime, sentence management and voice reach full statement coverage, while Silver remains blocked by the greater-than-95% requirement.
