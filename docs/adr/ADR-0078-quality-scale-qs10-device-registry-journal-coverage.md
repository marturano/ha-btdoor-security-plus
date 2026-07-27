# ADR-0078: QS-10 Device Registry and Journal Coverage

## Status

Accepted

## Decision

Add behavioural tests for device visibility cleanup, registry creation and metadata migration, localized registry reports, topology validation, and the complete persistent Call Journal lifecycle including rebuild, metrics, terminal events and storage self-healing.

Coverage evidence is produced by a completed pytest-cov run. Certification launchers that execute nested subprocess suites remain validated in isolated processes.

## Consequences

Measured integration coverage rises from 76.56% to 79.23%. Device registry lifecycle reaches full statement coverage, device topology reaches 85%, and the Call Journal reaches 94%. Silver remains blocked by the greater-than-95% requirement.
