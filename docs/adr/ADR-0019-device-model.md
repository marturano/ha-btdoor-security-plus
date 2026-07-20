# ADR-0019 — Logical Device Model

## Status
Accepted for 5.0.0-beta.2.

## Context
Before Beta.2 every entity was attached to a single legacy SIP-client device. This hid the separation between the physical gateway and the Cloud, SIP, Dialog, Media, and Diagnostic runtimes.

## Decision
One configuration entry exposes a stable gateway root and five child service devices:

- Gateway
- Cloud Runtime
- SIP Runtime
- Dialog Runtime
- Media Runtime
- Diagnostic Engine

Child devices use `via_device` to reference the gateway. Entity `unique_id` values remain unchanged. The gateway keeps the legacy `sip_client_<id_device>` identifier in addition to the new identifier, allowing Home Assistant to merge the existing registry device instead of creating an orphan.

A central `device_model` package owns identifiers, metadata, and registry creation. Entity base classes select a `DeviceKind`; individual entities override it only where needed.

## Consequences
The Home Assistant device page becomes easier to navigate and is ready for the 2026.7 full-page device experience. Existing entity history and automations remain tied to unchanged entity unique IDs. Multiple config entries remain isolated because every new identifier includes the config-entry unique key.
