# Diagnostics and Support Architecture

## Components

- Runtime state provider: normalized snapshot for entities and support consumers.
- Health Score: weighted provider results with timeout isolation and explanations.
- Event metrics and timeline: compact counters and bounded histories.
- Call journal: event-driven call records and derived summaries.
- Persistent media snapshots: retained diagnostic metadata, not unrestricted recordings.
- Developer Toolkit: opt-in runtime inspector, event monitor, metrics and support actions.
- Support Bundle v2: private, sanitized diagnostic artifact.

## Privacy and safety

All structured exports pass through the central sanitizer. Secrets, credentials, certificate/key paths and sensitive identifiers are removed, redacted or hashed. Journal exports remain private under the integration storage/export area and are not exposed through `/local`.

## Registry evidence

Support Bundles include sanitized device/entity registry evidence to diagnose duplicates, visibility, disabled state, topology, user names and areas. Runtime evidence does not replace source code and must not be used to claim tests that were not performed.
