# ADR-0073: QS-5 Core, Media and SIP Coverage

## Status
Accepted

## Context
After QS-4, measured integration coverage was 59.24%. Core storage helpers, media negotiation and a substantial part of SIP parsing/authentication still lacked direct behavioural regression tests.

## Decision
Add deterministic tests that execute the real `__init__.py`, `media.py` and `sip_client.py` modules with minimal Home Assistant stubs only where required. Cover pure protocol and storage behaviour before network transport paths. Do not alter runtime logic merely to increase coverage.

## Consequences
- Certificate material migration helpers and legacy entity cleanup are regression protected.
- SDP/SRTP preparation and redaction behaviour are regression protected.
- SIP parser and digest-authentication helpers are regression protected.
- Overall coverage rises to 64.62%, while Silver remains blocked until measured coverage exceeds 95%.
