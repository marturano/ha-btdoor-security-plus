# ADR-0085: QS-17 developer and lifecycle residual coverage

## Status

Accepted — 2026-07-23

## Context

After QS-16 the integration had 90.50% measured coverage. Developer diagnostics still contained unexecuted production paths for cloud, SIP, TLS and certificate inspection. These paths are operationally important because they are used to diagnose target installations and generate trustworthy support evidence.

## Decision

Add behavioural tests that execute the real Developer Tools diagnostic contracts with controlled cloud, SIP and TLS collaborators and a real generated X.509 certificate. Keep module isolation explicit so synthetic Home Assistant modules cannot leak into platform tests.

## Consequences

- measured integration coverage increases to 91.06%;
- `developer.py` increases to 84.67%;
- diagnostic cloud, SIP, TLS and certificate paths are executable and regression-protected;
- Silver remains blocked until measured integration coverage strictly exceeds 95%.
