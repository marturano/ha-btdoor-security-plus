# Compatibility Certification

Compatibility certification covers repository metadata and target-runtime behavior separately.

## Repository checks

- `manifest.json` structure and version;
- `hacs.json` structure;
- pinned Python requirements;
- config flow declaration;
- integration domain consistency;
- translation and platform file presence;
- package import and test execution.

## Target checks required for Final

- clean install on supported Home Assistant 2026.x;
- migration from the previous supported release;
- reload and restart;
- HACS installation and update;
- rollback to the previous release;
- device/entity continuity;
- diagnostics and support-bundle generation.
