# ADR-0072: QS-4 Services and Cloud Coverage

## Status
Accepted

## Context
After QS-3, total measured coverage was 53.24%. The service layer and cloud provisioning client contained important operational and error-handling paths with no executable coverage.

## Decision
Add isolated behavioural tests that execute the real `services.py` and `cloud.py` modules with minimal Home Assistant stubs and deterministic collaborators. Do not alter runtime behaviour merely to improve the score. Continue to use measured pytest-cov evidence as the only basis for Quality Scale promotion.

## Consequences
- Global service registration, targeting, responses and failure translation are regression protected.
- Cloud parsing, authentication classification, gateway discovery, SIP-user logic and certificate-file handling are regression protected.
- Overall coverage rises to 59.24%, but Silver remains blocked until coverage exceeds 95%.
