# GitHub Sandbox and Ruff Remediation Report — 2026-07-27

## Scope
Implementation of the permanent GitHub Sandbox Validation Gate and preparation of RC15 for authoritative Ruff remediation in GitHub Actions.

## Implemented
- Read-only GitHub sandbox validation workflow.
- Manually dispatched Ruff remediation workflow.
- Canonical validation shell runner with versioned evidence.
- ADR-0091, operational guide, governance registry, quality gates, impact matrix, engineering notebook and handoff updates.
- Required Quality Scale remains GOLD and cannot be downgraded as remediation.

## Local validation evidence
- Python compilation: PASS.
- Repository test suite: progressed through all test groups; targeted release, integrity, distribution, audit, certification and target-validation tests: 22 PASS.
- Publication preflight: PASS.
- Repository integrity: PASS.
- Document consistency: PASS.
- Repository hygiene: PASS after removing test-generated empty work directories.
- Governance suite: PASS across all reported gates.
- Certification framework: PASS.
- Final certification: BLOCKED, expected, because external GitHub/HACS/Hassfest and corrected latest-Ruff evidence are not yet imported.

## Ruff status
The existing GitHub log demonstrates Ruff violations in RC15. The current execution environment cannot retrieve the official Ruff package, so this package is not represented as Ruff-clean. The repository now contains an authoritative remediation workflow that installs the latest stable official Ruff release, applies supported fixes and formatting, runs the complete validation suite, commits only after success, and is followed by a read-only validation workflow.

## Required next action
1. Push this package to the publication branch.
2. Manually dispatch `Ruff Remediation`.
3. Review the generated commit and artifact.
4. Require `GitHub Sandbox Validation` and all existing publication workflows to pass.
5. Import evidence and only then generate the next RC package.
