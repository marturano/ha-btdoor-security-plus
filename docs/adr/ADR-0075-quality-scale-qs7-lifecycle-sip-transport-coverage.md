# ADR-0075: QS-7 Lifecycle and SIP Transport Coverage

## Status
Accepted

## Decision
Add behavioural tests for SIP lifecycle, transport, authentication, command retry, session teardown and call rejection. Merge the new isolated pytest-cov evidence with the previously validated full-suite coverage evidence by executed line.

## Rationale
The SIP client is the largest remaining coverage deficit. Line-union evidence is deterministic and avoids claiming coverage for code that was not executed.

## Consequences
Coverage rises to 71.57%, while the Quality Scale remains Bronze because the Silver threshold is still not met.
