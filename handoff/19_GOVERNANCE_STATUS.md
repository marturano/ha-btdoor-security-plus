# Governance Status

Release: **1.1.0-rc.15**

- Project Governance Charter: active.
- Project Execution Contract: active and extended for integrity gates.
- Repository Policy: active.
- Definition of Ready: mandatory.
- Definition of Done: mandatory.
- Archive-before-replacement: mandatory.
- Breaking-change ADR and migration plan: mandatory.
- Zero Knowledge Loss continuity: mandatory.

## Governance closure extension — 2026-07-22

The workflow now formally includes Engineering Notebook, Translation Review, Benchmark Review, documented Quality Reviews, maintained Security Policy, Automation Assets Review, Release Documentation and mandatory HACS/GitHub publication validation for Final Releases.

## Canonical policy locations

- Constitution: `docs/project/PROJECT_CONSTITUTION.md`
- Repository policy: `docs/repository/REPOSITORY_POLICY.md`
- Quality policy: `docs/quality/QUALITY_POLICY.md`
- Benchmark policy: `docs/benchmarks/BENCHMARK_POLICY.md`
- Release documentation policy: `docs/release/RELEASE_DOCUMENTATION_POLICY.md`

Legacy root policy documents were archived after their unique content was consolidated.

## Effective-validation rule

Workflow syntax is no longer accepted as governance evidence. A gate may be marked PASS only when the command has run against the exact repository tree and has returned exit code `0`. FAIL, NOT VERIFIED and BLOCKED must be preserved honestly. The canonical contract is `docs/validation/GITHUB_ACTIONS_VALIDATION.md`, enforced by `tools/validation/check_github_workflows.py`.
