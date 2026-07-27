# ADR-0086: QS-18 media residual coverage

## Status

Accepted — 2026-07-23

## Context

After QS-17 the integration had 91.06% measured coverage. Media negotiation still had uncovered error handling around malformed SRTP keys, socket allocation failures, route discovery and partial preparation cleanup.

## Decision

Add behavioural tests that execute these media edge paths with controlled sockets and deterministic key generation. Tests validate redaction and lifecycle behaviour without exposing key material or opening real network media sessions.

## Consequences

- measured integration coverage increases to 91.49%;
- `media.py` increases to 99.16%;
- media failure cleanup and SRTP metadata handling are regression-protected;
- Silver remains blocked until measured integration coverage strictly exceeds 95%.
