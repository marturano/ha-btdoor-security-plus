# ADR-0091 — GitHub Sandbox Validation Gate

## Status
Accepted — permanent release governance rule.

## Decision
Every Release Candidate and Final release must be validated in a clean GitHub-hosted sandbox using Python 3.13, the latest stable Ruff release available from the official Python package channel, and every repository validation tool required by the release pipeline.

The validation gate must execute Ruff formatting and lint checks, compilation, the complete pytest suite, publication preflight, repository integrity, documentation consistency, repository hygiene, governance, certification, HACS/Hassfest checks when configured, and the Home Assistant Integration Quality Scale gate.

A separate manually dispatched remediation workflow may apply Ruff's supported automatic fixes and formatter, but it must subsequently run the complete validation suite. The normal validation workflow never modifies code and must fail if the repository is dirty or any gate fails.

## Non-negotiable constraints
- No release while any mandatory check fails.
- No global suppression or weakening of Ruff rules to obtain a passing result.
- No reduction of the project's required Integration Quality Scale level.
- The current required release level remains GOLD until an explicit governed decision changes it.
- Evidence must identify exact Python and Ruff versions and be retained with release evidence.

## Consequences
GitHub is the authoritative external validation environment. Local validation remains mandatory where available, but cannot replace the clean GitHub sandbox evidence required for RC or Final approval.
