# Quality Gates

A stable release requires version consistency, static validation, focused and full regression tests, translation parity, documentation coverage, compatibility evidence, sanitized diagnostics, security review and migration notes.

Future Home Assistant versions are marked planned until released and tested.

## GitHub Sandbox Validation Gate

Before every RC or Final package is approved, the exact release commit must pass `.github/workflows/github-sandbox-validation.yml` in a clean GitHub-hosted runner. The gate installs the latest stable official Ruff release at execution time, records its version, and runs formatting, lint, compilation, tests, publication, integrity, documentation, hygiene, governance and certification checks.

Failures must be remediated rather than ignored. `.github/workflows/ruff-remediation.yml` may be manually dispatched to apply Ruff-supported fixes in GitHub, but approval requires a subsequent clean read-only validation run. Ruff rule suppression and Quality Scale downgrades are not valid remediation. The project release threshold remains GOLD.

## Validation evidence semantics

Workflow parsing, YAML acceptance and command presence are prerequisites, not validation results. The authoritative definitions of PASS, FAIL, NOT VERIFIED and BLOCKED, together with the exact GitHub Actions sequence, are maintained in [GitHub Actions Validation Contract](../validation/GITHUB_ACTIONS_VALIDATION.md).

Every mandatory command must preserve its exit code through logging pipelines. The canonical runner therefore uses `set -euo pipefail`, explicit Bash invocation and a logged-command wrapper. A release remains blocked while HACS, Hassfest, Ruff, mypy, pytest, compatibility, governance or certification is not verified against the exact release tree.
