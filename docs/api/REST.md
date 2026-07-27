# REST API — Planned

## Status

Contract-only roadmap item for the 3.x Developer Platform. RC.15 does not register BTDoor-specific REST endpoints.

## Design requirements

- explicit API version;
- Home Assistant authentication and authorization;
- idempotency/correlation keys for commands;
- one unambiguous target per physical action;
- structured errors;
- rate limiting and auditability;
- no credential, certificate or raw-media leakage;
- OpenAPI schema and conformance tests before public release.

Home Assistant's existing REST API can call services/actions and read entities, but its behavior is governed by Home Assistant and is not a BTDoor-specific REST compatibility contract.
