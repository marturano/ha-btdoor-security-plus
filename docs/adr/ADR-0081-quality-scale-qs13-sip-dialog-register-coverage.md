# ADR-0081: QS-13 SIP Dialog and Registration Coverage

## Status

Accepted

## Decision

Add behavioural tests for SIP dialog establishment and termination, registration authentication, keepalive and response generation without changing production behaviour.

## Rationale

The remaining SIP client deficit contained critical protocol lifecycle paths. Executing INVITE, CANCEL, BYE, REGISTER and timeout behaviour provides stronger release evidence than source inspection or mocked line-only assertions.

## Consequences

Measured integration coverage is **87.63%**. `sip_client.py` reaches approximately **82%** coverage. Silver remains blocked until total integration coverage exceeds 95%.
