# ADR-0011 — Certificate Migration and Health Isolation

- **Status:** Accepted
- **Release:** 4.0.0-alpha.24

## Context

After the domain rename, existing installations could retain client certificate material under `custom_components/btdoor_entry_plus/certificate/<gateway>`. The config entry could point to the new domain while the files remained in the old directory. Developer tests then reported `certificates`, `tls`, and `health` as failed even when an already-established SIP/TLS session was still active.

## Decision

1. Migrate certificate material from every known legacy domain into `custom_components/btdoor_security_plus/certificate/<gateway>`.
2. Read certificate paths from the live SIP client in Developer Tools, with config-entry fallback.
3. Keep the certificate inspection test strict, but make aggregate Health non-raising.
4. Derive TLS runtime health from the live registered SIP session rather than from certificate file inspection.
5. Report failures independently to prevent diagnostic cascades.

## Consequences

Existing installations recover their certificate material automatically at setup. A genuinely missing certificate remains visible, while a live TLS session is no longer misreported solely because a separate file-inspection test failed.
