# Runtime and Release Certification Policy

**Status:** Canonical certification policy  
**Applies to:** Release Candidates and Final Releases

## Principle

Certification evidence must state the environment in which it was collected. Repository-local evidence never substitutes for execution on a supported Home Assistant installation.

## Certification classes

1. **Repository certification** — manifests, metadata, schemas, imports, tests, security patterns and package structure.
2. **Local runtime certification** — repeatable execution inside the current Python environment, including test duration and process resource observations.
3. **Home Assistant runtime certification** — clean install, startup, reload, update, rollback, entity registration and sustained operation on a supported Home Assistant version.
4. **Publication certification** — GitHub tag/release/assets/checksum and HACS install/update/rollback.

Only classes actually executed may be marked validated. Missing target infrastructure is a documented blocker, not a pass.

## Required outputs

- `certification_environment.json`
- `runtime_certification.json`
- `compatibility_certification.json`
- `security_certification.json`
- `ux_accessibility_certification.json`
- `release_certification.json`
- matching Markdown reports in `docs/certification/reports/`

## Final-release rule

The Final Release Gate requires all blocking certification items to be validated and all CRITICAL/HIGH risks closed or explicitly accepted through a recorded decision.
