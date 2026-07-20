# ADR-0009 — Support artifact naming and legacy compatibility

- **Status:** Accepted
- **Date:** 2026-07-17
- **Software version:** 4.0.0-alpha.22

## Context

The Home Assistant domain was renamed to `btdoor_security_plus`, but the developer support generator still created files using the historical `BTDoorPlus_Support` prefix. Retention also searched only for that old prefix.

## Decision

New reports use:

- `BTDoorSecurityPlus_Support_<UTC timestamp>.md`
- `BTDoorSecurityPlus_Support_<UTC timestamp>.zip`

Naming is centralized in `support_naming.py`. Cleanup and retention recognize the current prefix and the historical `BTDoorPlus_Support` and `BTDoorEntryPlus_Support` prefixes.

## Consequences

- Newly generated files reflect the current project identity.
- Existing support files remain manageable after upgrade.
- Retention cannot fail merely because a directory contains legacy report names.
- Future naming changes have a single implementation point and regression tests.
