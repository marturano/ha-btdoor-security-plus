# Release Publication Status

- Every Final Release must pass HACS and GitHub Publication Validation.
- Canonical runbooks are under `docs/repository/`.
- `docs/repository/validations/1.1.0-final.md` is intentionally pending.
- Do not declare 1.1.0 Final until online repository, release asset, HACS clean install, upgrade and rollback evidence is recorded.

## GitHub Sandbox Validation status — 2026-07-27
- Permanent validation and remediation workflows: IMPLEMENTED in repository.
- Latest stable Ruff validation evidence for the corrected commit: PENDING GitHub execution.
- RC15 publication decision: BLOCKED until remediation and subsequent read-only validation pass.
- Required Integration Quality Scale: GOLD, unchanged.

## GitHub validation prerequisite — 2026-07-27

Publication remains blocked. The updated commit must pass HACS, Hassfest, canonical Python/governance validation, all configured Home Assistant compatibility jobs, GitHub Sandbox Validation and Governance. Artifacts and run identifiers must identify the same commit from which the release ZIP is generated.
