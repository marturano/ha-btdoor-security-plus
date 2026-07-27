# ADR-0080: QS-12 Cloud and SIP Dispatch Coverage

## Status

Accepted

## Decision

Add behavioural tests for residual cloud transport and SIP dispatch branches without changing production behaviour.

## Rationale

These modules held the largest remaining executable coverage deficits. Testing protocol branches and transport failures provides higher confidence than source-only assertions.

## Consequences

Measured integration coverage is 83.22%. Silver remains blocked until coverage exceeds 95%.
