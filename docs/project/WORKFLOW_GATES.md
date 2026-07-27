# Workflow Gates

**Status:** Authoritative gate catalogue  
**Owner:** Project Maintainer  
**Evidence rule:** every gate decision must identify its evidence, decision, blockers, exceptions and next action.

| Gate | Entry criteria | Exit criteria | Blocking examples | Canonical evidence |
|---|---|---|---|---|
| Definition of Ready Gate | Scope and roadmap item identified | Acceptance criteria, risks, dependencies, test and documentation impacts are explicit | Undefined scope, missing owner, unknown migration impact | Definition of Ready, Engineering Notebook |
| Architecture Gate | Design and architecture review completed | Boundaries and contracts are accepted; ADR status resolved | Unreviewed public contract, ownership ambiguity | Architecture docs, ADR register |
| Quality Gate | Self review, code review, static analysis and test layers evaluated | Required checks pass or exceptions are accepted | Failing tests, untriaged lint errors, missing regression coverage | Quality dossier, test report |
| Security Gate | Security-impact classification completed | Threats, secrets, privacy, dependencies and physical actions are accepted | Secret exposure, unsafe physical action, unresolved critical vulnerability | Security review and policy |
| Performance Gate | Performance impact classified | Benchmarks meet thresholds or regression is accepted | Unexplained regression, missing baseline for material change | Benchmark report and baseline |
| Documentation Gate | Product and repository documentation reviewed | User, developer, API, translation, compatibility and assets are current | Broken links, undocumented behavior, stale examples | Documentation review and registers |
| Home Assistant Quality Scale Gate | Initial and final assessment, desired-tier plan and remediation verification completed | Configured release minimum is achieved; gaps to desired tier are documented with owners/evidence needs | Tier below release minimum, unproven completion, missing remediation plan, stale report | `docs/quality-scale/QUALITY_SCALE_REPORT.json`, `QUALITY_SCALE_WORKFLOW_STATUS.json`, `QUALITY_SCALE_REMEDIATION_PLAN.json` |
| Validation Gate | QA and affected checks executed | Canonical validation report/register match the package | Fragmented evidence, failed integrity check, stale validation | `docs/validation/` |
| Release Readiness Gate | All previous gates resolved and dashboard refreshed | Release candidate is complete enough for publication assessment | Open blocker, inconsistent version, incomplete handoff | Release checklist, dashboard, handoff |
| Publication Gate | Assets, version, tag and repository instructions reviewed | Publication package is reproducible and maintainable | Missing checksum, invalid manifest, missing rollback instructions | Publication runbook and validation |
| Final Release Gate | Final HACS/GitHub lifecycle validation completed | Final release approved for publication | Failed HACS validation, untested installation/upgrade, unresolved blocker | Final release dossier and HACS/GitHub report |

## Gate decision states

- **PASS:** all mandatory criteria are satisfied.
- **PASS WITH CONDITIONS:** non-blocking actions are accepted with owner and due point.
- **BLOCKED:** one or more release-blocking criteria are unresolved.
- **NOT APPLICABLE:** applicability was reviewed and the rationale is recorded.
- **NOT STARTED:** required evidence does not yet exist.

## Exception rule

An exception must never be implicit. It must identify the affected gate, risk, rationale, owner, expiry or review point, mitigation and acceptance authority.

## Evidence-backed gate rule

Every PASS or PASS WITH CONDITIONS decision must reference validated evidence IDs from `docs/quality/evidence_register.json`. Release Readiness and Final Release decisions must also evaluate `risk_register.json`; open CRITICAL or HIGH risks require closure or a formally documented exception.
