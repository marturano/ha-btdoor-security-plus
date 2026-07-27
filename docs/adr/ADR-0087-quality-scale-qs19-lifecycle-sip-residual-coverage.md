# ADR-0087: QS-19 lifecycle and SIP residual coverage

## Status

Accepted.

## Decision

Add behavioural tests for Home Assistant lifecycle helpers and SIP stream framing rather than import-only coverage. Preserve strict module isolation so synthetic Home Assistant modules cannot leak into platform tests.

## Consequences

Measured integration coverage rises from 91.49% to 92.55%. Silver remains blocked until coverage strictly exceeds 95%.
