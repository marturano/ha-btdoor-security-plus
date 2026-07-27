# ADR-0088: QS-20 Silver achievement

## Status

Accepted.

## Decision

Close the Silver coverage rule only after a completed full pytest-cov run reports integration coverage strictly above 95%. Add behavioural coverage for setup-entry orchestration, Support Bundle generation, SIP SDP/Digest residuals and stable package exports without changing production runtime behaviour solely for coverage.

## Consequences

Measured integration coverage rises from 92.55% to 95.08%. All Silver rules are complete and the repository Quality Scale self-assessment advances to Silver. Gold remains incomplete because translatable exception evidence is still open.
