# BTDoor Security+ 6.0.1

BTDoor Security+ 6.0.1 is a diagnostics-only maintenance release.

## Fixed

- `sip/timeline-summary.json` now classifies SIP requests from the persisted `line` field, including `INVITE`, `CANCEL`, `MESSAGE`, `REGISTER`, `BYE`, and other standard methods.
- SIP responses are grouped by status class: `1xx`, `2xx`, `3xx`, `4xx`, `5xx`, and `6xx`.
- Existing timeline records with explicit `event` or `type` fields remain supported.

## Runtime impact

There are no changes to Cloud authentication, certificate provisioning, SIP transport, registration, call handling, RTP/SRTP preparation, gate control, Home Assistant entities, services, Device Registry identifiers, or stored configuration.

## Validation target

After upgrading, generate a new Support Bundle and verify that the sum of `events_by_type` equals `event_count` and that recognized SIP records are no longer reported as `unknown`.
