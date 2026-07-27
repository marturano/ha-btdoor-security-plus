# Repository Hygiene Audit — 1.1.0 RC15

**Date:** 2026-07-23  
**Scope:** pre-Phase 7C repository audit  
**Classification:** documentation, governance and packaging hygiene only  
**Runtime impact:** none

## Result

The repository hygiene audit identified transient and packaging-only residue that was not required by runtime, tests, documentation, HACS, GitHub Actions or the active governance system.

## Archived outside the canonical repository package

| Path | Classification | Resolution |
|---|---|---|
| `.coverage` | transient local test database | preserved in the companion hygiene archive and removed from the canonical repository |
| `dist/btdoor-security-plus-1.1.0-rc.15.zip` | nested release archive | preserved in the companion hygiene archive and removed from the canonical repository |
| `dist/btdoor-security-plus-1.1.0-rc.15.zip.sha256` | checksum for nested archive | preserved in the companion hygiene archive and removed from the canonical repository |

The nested archive removal enforces `docs/repository/REPOSITORY_POLICY.md`, which excludes nested release archives and transient output from release packages.

## Removed as non-artifact workspace residue

- empty `ha-certification-work/` directory;
- empty `target-validation-work/` directory;
- Python `__pycache__/` directories and `.pyc` files generated during local validation.

Empty work directories and interpreter caches contain no project history and are therefore not historical archive material.

## Retained after review

- `dist/btdoor-security-plus-1.1.0-rc.15.release.json`, retained as structured release evidence;
- `docs/platinum/` and QS-22 records, retained as explicitly historical analysis referenced by the Gold policy and accepted ADR trail;
- `PROJECT_MANIFEST.yaml`, `hacs.json` and `pyproject.toml`, retained because they are convention-loaded or operational repository files even when ordinary Markdown references are absent.

## Single Source of Truth assessment

No exact Markdown duplicate groups were detected. Platinum material is non-normative historical evidence; the authoritative policy remains `docs/quality-scale/QUALITY_SCALE_POLICY.md`, which fixes Gold as the minimum, desired and maximum governed tier.

## Phase 7C status

This hygiene audit does not approve Phase 7C. Quality Scale and Release Readiness checks pass, but the Release Decision Engine remains `BLOCKED` until its listed security, performance, UX, compatibility, publication and target Quality Scale evidence blockers are closed with exact-package certificates.
