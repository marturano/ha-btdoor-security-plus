# Quality Gates

A stable release requires version consistency, static validation, focused and full regression tests, translation parity, documentation coverage, compatibility evidence, sanitized diagnostics, security review and migration notes.

Future Home Assistant versions are marked planned until released and tested.

## GitHub Sandbox Validation Gate

Before every RC or Final package is approved, the exact release commit must pass `.github/workflows/github-sandbox-validation.yml` in a clean GitHub-hosted runner. The gate installs the latest stable official Ruff release at execution time, records its version, and runs formatting, lint, compilation, tests, publication, integrity, documentation, hygiene, governance and certification checks.

Failures must be remediated rather than ignored. `.github/workflows/ruff-remediation.yml` may be manually dispatched to apply Ruff-supported fixes in GitHub, but approval requires a subsequent clean read-only validation run. Ruff rule suppression and Quality Scale downgrades are not valid remediation. The project release threshold remains GOLD.
