# Test Status

## Current Linux validation checkpoint — 2026-10-27

Ruff/format, mypy, 347 pytest tests, fresh coverage 95.01%, all 18 governance subchecks, publication, integrity, hygiene and the canonical runner PASS on Ubuntu/Python 3.14.2. Real HA 2026.7.2 import/API smoke PASS. Historical local failures below are superseded for this code. Remote commit checks and live target certification remain separate; Final remains BLOCKED.

See [the Linux validation report](../docs/validation/LINUX_VALIDATION_2026-10-27.md).


## Current Ruff checkpoint — 2026-10-27

Ruff: 77 to 0; format check passes. Windows/Python 3.12 pytest: 337 passed, 3 existing failures reproduced on the original ZIP. mypy executed and failed (160 diagnostics, including missing Home Assistant imports). Fresh coverage, Linux CI, remote checks and live HA/SIP/Cloud remain unverified. Final remains BLOCKED. Historical full-pass and coverage claims do not validate this edited package.

See [the current validation report](../docs/validation/RUFF_RESIDUAL_REMEDIATION_2026-10-27.md).

RC.14 validation covers version consistency, required PCP files, roadmap content, archive traceability, translation document presence, syntax, and existing documentation QA.

The full Home Assistant-dependent suite may be limited in a standalone build environment. Any such limitation must be recorded in the release validation report and must not be represented as a passing runtime validation.

## Full-suite limitation observed in Phase 4

The focused RC.15 Phase 1–4 suite passes (13 tests). The legacy full repository suite is not a release-pass signal in this isolated environment: three modules fail collection because Home Assistant/runtime package surfaces are unavailable, and the remaining broad run reports 17 historical failures, mostly stale release-version assertions plus pre-existing runtime/import expectations. Phase 4 changes are documentation, governance, tests and integrity tooling only; these failures were not introduced or hidden. They must be triaged during stabilization with a real Home Assistant test environment.

## 2026-07-27 — Effective GitHub validation remediation

The updated repository now has a dependency-free workflow contract validator and one canonical read-only validation runner. Local evidence is limited to the checks actually executed:

| Gate | Status | Evidence |
|---|---|---|
| Workflow contract | PASS | `python tools/validation/check_github_workflows.py` |
| New validation tooling compilation and Bash syntax | PASS | local execution |
| Repository integrity checks, individually | PASS | local execution of every named integrity check |
| Ruff | NOT VERIFIED | package index returned HTTP 503 |
| mypy | NOT VERIFIED | package index returned HTTP 503 |
| Full pytest suite | NOT VERIFIED | local command window expired before completion |
| HACS / Hassfest | NOT VERIFIED | requires GitHub-hosted execution |
| HA compatibility matrix | NOT VERIFIED | requires updated GitHub-hosted execution |

Release status remains BLOCKED until the updated exact commit produces green mandatory GitHub jobs.
