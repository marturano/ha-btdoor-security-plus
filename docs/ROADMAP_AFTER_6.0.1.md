# Recommended improvements after 6.0.1

These items are intentionally excluded from the diagnostics-only 6.0.1 maintenance release.

## Priority 1 — Security

- Add opt-in server certificate verification and a safe migration path from `verify_server: false`.
- Document trusted CA-chain configuration and certificate renewal failure recovery.

## Priority 2 — Support Bundle completeness

- Export sanitized Entity Registry and Area Registry relationships.
- Add a machine-readable bundle schema version and compatibility validator.
- Add per-provider execution time and timeout metadata.

## Priority 3 — Quality and maintainability

- Reduce Ruff debt incrementally, one module per pull request.
- Add Home Assistant fixture-based integration tests for setup, unload, reload, and migration.
- Add contract tests that compare `strings.json` with every translation file.

## Priority 4 — SIP diagnostics

- Add optional counts by direction (`in`/`out`) and method/status without changing raw timeline retention.
- Track unrecognized lines with sanitized examples and a bounded sample count.
- Add session-level summaries while preserving the existing aggregate file.

## Priority 5 — Distribution

- Make the repository public when ready for HACS custom repository installation.
- Add issue and pull-request templates and a public support policy.
