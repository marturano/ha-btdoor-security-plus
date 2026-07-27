# Test Status

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
