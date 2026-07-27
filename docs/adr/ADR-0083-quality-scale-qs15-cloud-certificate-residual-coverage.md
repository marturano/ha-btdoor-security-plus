# ADR-0083: QS-15 Cloud Certificate Residual Coverage

## Status

Accepted.

## Context

After QS-14, measured integration coverage was 88.42%. The cloud module still contained substantial uncovered certificate-generation, decoding, chain-processing and provisioning branches.

## Decision

Add deterministic behavioural tests against the real cloud certificate helpers and provisioning orchestration. Generate real RSA keys and X.509 certificates in the test process, exercise PEM, DER and ZIP inputs, and preserve production behaviour.

## Consequences

Measured integration coverage rises to 90.13%. `cloud.py` reaches 95.57%. Silver remains blocked by the strict greater-than-95% integration coverage threshold.
