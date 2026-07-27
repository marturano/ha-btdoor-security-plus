# Validation Register

| Validation domain | Current evidence | Status | Required next update |
|---|---|---|---|
| Repository integrity | `VALIDATION_REPORT_1.1.0-rc.15.md` | Current static evidence | Any repository structure or tooling change |
| Tests and QA | `VALIDATION_REPORT_1.1.0-rc.15.md` | Current for packaged RC | Any implementation change |
| Documentation and links | `VALIDATION_REPORT_1.1.0-rc.15.md` | Current | Any documentation change |
| Roadmap and ADR integrity | `VALIDATION_REPORT_1.1.0-rc.15.md` | Current | Any roadmap/ADR change |
| Architecture, ecosystem, AI and API | `VALIDATION_REPORT_1.1.0-rc.15.md` | Current static evidence | Any contract change |
| Translation | `VALIDATION_REPORT_1.1.0-rc.15.md` and `../i18n/TRANSLATION_REVIEW.md` | Current static evidence | Any string or locale change |
| Compatibility | `VALIDATION_REPORT_1.1.0-rc.15.md` and compatibility matrices | Partial; runtime proof still release-specific | Final runtime matrix execution |
| Benchmark | `../benchmarks/reports/1.1.0-rc.15.md` | Baseline record | Any performance-relevant change |
| Security | Security review documents | Maintained policy; release evidence required | Any security-relevant change |
| Handoff continuity | `VALIDATION_REPORT_1.1.0-rc.15.md` | Current | Every package build |
| GitHub/HACS publication | `../repository/validations/1.1.0-final.md` | Pending Final Release | Before Final publication |

| Project Health Dashboard | `../project/PROJECT_HEALTH_DASHBOARD.md` | Current for this package | After any gate or evidence change |

## Maintenance record

- **2026-07-22:** gate-based workflow and generated Project Health Dashboard introduced; dashboard added to validation maintenance.
- **2026-07-22:** fragmented RC.15 integrity and QA reports consolidated into one canonical validation report; historical archive removed; Validation Maintenance and Update gate introduced.

## Phase 6A Governance Automation

| Validation | Tool | Evidence | Status |
|---|---|---|---|
| Governance structure | `tools/governance/check_governance.py` | `docs/project/GOVERNANCE_AUTOMATION.md` | Implemented |
| Handoff continuity | `tools/handoff/check_handoff.py` | `handoff/` | Implemented |
| Release readiness structure | `tools/release/check_release_readiness.py` | release and validation documents | Implemented |
| Health and compliance | `tools/health/calculate_health.py` | `project_health_calculated.json` | Implemented |
| Consolidated execution | `tools/governance/run_governance.py` | `governance-automation-report.json` | Implemented |

## Phase 6B — Repository Rationalization

| Check | Evidence | Status |
|---|---|---|
| Canonical registry completeness | `docs/project/canonical_documents.json` | PASS |
| Markdown reference integrity | `docs/project/repository_metrics.json` | PASS |
| Exact active-document duplicate detection | `docs/project/repository_metrics.json` | PASS |
| Dependency map generation | `docs/project/repository_dependency_map.json` | PASS |
| Governance integration | `docs/validation/governance-automation-report.json` | PASS |

## Phase 6C — Quality and Release Intelligence

| Check | Evidence | Status |
|---|---|---|
| Evidence registry integrity | `../quality/quality_release_intelligence.json` | Implemented |
| Risk-to-evidence consistency | `../quality/risk_register.json` | Implemented |
| Technical debt separation | `../quality/technical_debt_register.json` | Implemented |
| Decision traceability | `../quality/DECISION_TRACEABILITY.md` | Implemented |
| Release decision explanation | `../quality/RELEASE_DECISION_REPORT.md` | Implemented; Final currently expected to remain BLOCKED |

## Phase 6D — Runtime and Release Certification

| Certification | Evidence | Status |
|---|---|---|
| Repository-local runtime | `../certification/runtime_certification.json` | VALIDATED |
| Repository metadata compatibility | `../certification/compatibility_certification.json` | VALIDATED |
| Repository security scan | `../certification/security_certification.json` | VALIDATED; target review pending |
| Structural UX/accessibility | `../certification/ux_accessibility_certification.json` | VALIDATED; interactive review pending |
| Home Assistant 2026.x runtime | `../certification/reports/RUNTIME_CERTIFICATION_REPORT.md` | PENDING target execution |
| HACS install/update/rollback | `../certification/reports/COMPATIBILITY_CERTIFICATION_REPORT.md` | PENDING target execution |
| Final release certification | `../certification/release_certification.json` | BLOCKED by five target evidence items |

## Target Validation Pack

- Framework: PASS
- Imported target runs: none
- Final target evidence: PENDING
- Validator: `python tools/target_validation/target_validation.py validate --run-id <id>`

### Phase 6E validation result

- Pytest: 200 passed
- Governance orchestrator: 12/12 PASS
- Repository hygiene: PASS
- Release certification: BLOCKED pending imported target evidence

| Phase 7B Home Assistant certification harness | PASS | Repository harness validated; live Home Assistant 2026.x execution remains pending |
