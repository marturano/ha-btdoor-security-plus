# ADR-0064: Home Assistant Certification Enablement

## Status
Accepted

## Decision
Use an executable, evidence-preserving certification harness for real Home Assistant 2026.x targets. Repository-only tests may validate the harness but may not be represented as runtime certification.

## Consequences
A live target, sanitized evidence and operator attestation are required before target validation can be imported and the release gates can change.
