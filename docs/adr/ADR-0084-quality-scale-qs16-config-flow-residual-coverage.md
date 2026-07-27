# ADR-0084: QS-16 Config Flow Residual Coverage

## Status

Accepted.

## Context

After QS-15, measured integration coverage was 90.13%. Config-flow helper branches for real cloud discovery, provisioning data construction, SIP validation, reauthentication failures and options normalization remained uncovered.

## Decision

Extend the existing contract-compatible config-flow harness with deterministic behavioural tests against the real `config_flow.py` implementation. Preserve production code and validate outcomes through cloud and SIP client doubles.

## Consequences

Measured integration coverage rises to 90.50%. `config_flow.py` reaches 95.40%. Silver remains blocked by the strict greater-than-95% integration coverage threshold.
