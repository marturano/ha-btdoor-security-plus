# Project Health Dashboard

**Status:** Governed, generated project artifact  
**Package:** `1.1.0-rc.15-phase7c-github-publication-ready`  
**Target:** `1.1.0 Final`  
**Last update:** `2026-07-23`  
**Source:** `docs/project/project_health.json`  
**Regenerate:** `python tools/health/calculate_health.py && python tools/update_project_health.py`

## Executive health

- **Governed assessment score:** **75/100 — WATCH**
- **Automated evidence-adjusted health:** **57/100**
- **Governance compliance score:** **100/100**
- **Blocking domains:** **1**
- **Domains not started:** **4**
- **Interpretation:** package integrity is strong, but Final Release readiness remains constrained by measured benchmarks, security/runtime evidence, compatibility execution and HACS/GitHub publication validation.
- **Approval semantics:** Release Readiness `PASS` confirms package-level readiness checks only; Final approval remains `BLOCKED` until the Release Decision Engine returns `APPROVED`.

## Domain scorecard

| Domain | Weight | Score | Status | Health | Next action |
|---|---:|---:|---|---|---|
| Governance | 8% | 96 | PASS | `██████████` | Maintain gate evidence during Final preparation. |
| Architecture | 10% | 90 | PASS WITH CONDITIONS | `█████████░` | Re-run Architecture Gate for any Final implementation change. |
| Quality | 12% | 82 | PASS WITH CONDITIONS | `████████░░` | Close blocking Final evidence and severe risks recorded by the release decision engine. |
| Security | 12% | 68 | NOT STARTED | `███████░░░` | Execute and document the Final security review. |
| Performance and Benchmark | 9% | 45 | BLOCKED | `████░░░░░░` | Establish measured reproducible baselines before Final readiness. |
| UX and Accessibility | 6% | 65 | NOT STARTED | `██████░░░░` | Create UX and accessibility evidence for dashboards and exposed controls. |
| Translation | 7% | 82 | PASS WITH CONDITIONS | `████████░░` | Complete Final translation verification and update the review. |
| Compatibility | 9% | 62 | NOT STARTED | `██████░░░░` | Execute the Final runtime compatibility matrix. |
| Documentation and Assets | 8% | 94 | PASS | `█████████░` | Maintain canonical registry and dependency metrics during Final preparation. |
| Validation | 8% | 94 | PASS | `█████████░` | Regenerate evidence after every package change. |
| GitHub and HACS Publication | 7% | 30 | NOT STARTED | `███░░░░░░░` | Run complete HACS and GitHub publication validation before Final. |
| Handoff and Continuity | 4% | 95 | PASS | `██████████` | Replace the handoff after the next meaningful milestone. |

## Blocking path to 1.1.0 Final

- **Performance and Benchmark — BLOCKED:** Establish measured reproducible baselines before Final readiness.
- **Security — NOT STARTED:** Execute and document the Final security review.
- **UX and Accessibility — NOT STARTED:** Create UX and accessibility evidence for dashboards and exposed controls.
- **Compatibility — NOT STARTED:** Execute the Final runtime compatibility matrix.
- **GitHub and HACS Publication — NOT STARTED:** Run complete HACS and GitHub publication validation before Final.

## Evidence map

### Governance

- `docs/project/PROJECT_CONSTITUTION.md`
- `docs/project/WORKFLOW.md`
- `docs/project/WORKFLOW_GATES.md`
- `docs/project/REPOSITORY_RATIONALIZATION.md`

### Architecture

- `docs/architecture/README.md`
- `docs/adr/README.md`

### Quality

- `docs/quality/QUALITY_REVIEW_REGISTER.md`
- `docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md`
- `docs/quality/evidence_register.json`
- `docs/quality/risk_register.json`
- `docs/quality/release_decision.json`

### Security

- `docs/security/SECURITY_POLICY.md`

### Performance and Benchmark

- `docs/benchmarks/BASELINES.md`
- `docs/benchmarks/reports/1.1.0-rc.15-governance.md`

### UX and Accessibility

- `docs/automation-assets/LOVELACE_GUIDE.md`

### Translation

- `docs/i18n/TRANSLATION_REVIEW.md`

### Compatibility

- `docs/validation/VALIDATION_REGISTER.md`

### Documentation and Assets

- `docs/project/REPOSITORY_INVENTORY.md`
- `docs/automation-assets/AUTOMATION_ASSETS_POLICY.md`
- `docs/project/CANONICAL_DOCUMENTS.md`
- `docs/project/REPOSITORY_DEPENDENCY_MAP.md`
- `docs/project/repository_metrics.json`

### Validation

- `docs/validation/VALIDATION_REGISTER.md`
- `docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md`

### GitHub and HACS Publication

- `docs/repository/validations/1.1.0-final.md`

### Handoff and Continuity

- `handoff/HANDOFF_INDEX.md`
- `handoff/28_IMMEDIATE_RESUME_POINT.md`

## Maintenance contract

1. Update the underlying review, register or report first.
2. Run `python tools/health/calculate_health.py`; do not hand-edit the calculated output.
3. Update `project_health.json` only from repository evidence; never from chat claims.
4. Regenerate this file after Validation Maintenance and Update, before Release Readiness, after gate changes and at release closure.
5. A dashboard score never overrides a blocked gate or missing mandatory evidence.
6. Record score-model changes in an ADR and in the Engineering Notebook.
