# Repository Cleanup Audit — 2026-07-22

## Scope

The full `1.1.0-rc.15` package was reviewed after governance consolidation.

## Actions

- removed the complete internal `docs/archive/` tree;
- removed deprecated compatibility pointer documents;
- removed archive-only engineering audits after preserving their current conclusions in canonical documents;
- consolidated fragmented RC.15 validation, integrity and QA evidence under `docs/validation/`;
- updated tests to validate canonical entry points rather than historical archive paths;
- removed empty directories, caches and generated local artifacts;
- added repository inventory and orphan checks;
- updated workflow, Definition of Done, Project Constitution, handoff and release records.

## Retention boundary

Files loaded by Home Assistant, HACS, GitHub Actions, pytest or repository conventions are not classified as orphaned merely because they lack a Markdown link. Dynamic platform modules, translations, custom sentences, brand assets, workflows, dashboards and blueprints are retained when their location is itself the contract.

## Result

The active package contains no internal archive tree and no deprecated pointer files. Validation evidence has a single policy, register and release report location.
