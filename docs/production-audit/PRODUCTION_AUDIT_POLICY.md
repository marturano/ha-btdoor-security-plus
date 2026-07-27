# Production Audit Policy

## Purpose

Phase 7A provides a reproducible repository-level audit before target certification and release approval.

## Mandatory controls

- Required project, HACS, and integration files exist.
- Manifest version follows a valid release identifier.
- Runtime requirements are exactly pinned.
- Code owners and HTTPS support URLs are declared.
- The HACS Home Assistant floor targets the 2026.x series.
- No cache, bytecode, editor backup, or temporary artifacts are committed.
- No likely credentials are present in supported text files.
- No unclassified exact duplicate production files exist outside documentation and generated distribution artifacts. Intentional Home Assistant string aliases and independently maintained locale files may be allowlisted explicitly.

## Gate boundary

Passing this audit does not change target evidence, certification, risk acceptance, or the Release Decision Engine. Publication remains blocked until every mandatory evidence and release gate is validated.
