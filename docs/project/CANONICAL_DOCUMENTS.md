# Canonical Documents Registry

**Generated:** 2026-10-27

This registry defines the single source of truth for each governed project area. Derived documents may summarize or operationalize canonical content but must not redefine it.

| Area | Canonical document | Owner | Derived artifacts |
|---|---|---|---|
| Project foundation | `docs/FOUNDATION.md` | Project governance | None |
| Project constitution | `docs/project/PROJECT_CONSTITUTION.md` | Project governance | `handoff/00_PROJECT_EXECUTION_CONTRACT.md` |
| Official workflow | `docs/project/WORKFLOW.md` | Project governance | `docs/project/WORKFLOW_GATES.md`, `handoff/24_OFFICIAL_WORKFLOW.md` |
| Definition of Ready | `docs/project/DEFINITION_OF_READY.md` | Project governance | None |
| Definition of Done | `docs/project/DEFINITION_OF_DONE.md` | Project governance | None |
| Product roadmap | `docs/roadmap/ROADMAP.md` | Product governance | `docs/roadmap/ROADMAP_1X.md`, `docs/roadmap/ROADMAP_2X.md`, `docs/roadmap/ROADMAP_3X.md`, `docs/roadmap/ROADMAP_4X.md`, `docs/roadmap/ROADMAP_5X.md`, `docs/roadmap/FUTURE_BACKLOG.md` |
| Architecture index | `docs/architecture/README.md` | Architecture | `ARCHITECTURE_PRINCIPLES.md` |
| Architecture decisions | `docs/adr/README.md` | Architecture | `docs/project/DECISIONS_AND_CONSTRAINTS.md` |
| Quality policy and register | `docs/quality/QUALITY_POLICY.md` | Quality | `docs/quality/QUALITY_REVIEW_REGISTER.md` |
| Security policy | `docs/security/SECURITY_POLICY.md` | Security | `SECURITY.md`, `docs/security/SECURE_DEVELOPMENT_GUIDE.md`, `docs/security/THREAT_MODEL.md`, `docs/security/SECURITY_BASELINE.md`, `docs/security/DATA_RETENTION.md` |
| Benchmark policy | `docs/benchmarks/BENCHMARK_POLICY.md` | Performance | `docs/benchmarks/BASELINES.md` |
| Translation review | `docs/i18n/TRANSLATION_REVIEW.md` | Localization | `docs/shared/terminology.yaml` |
| Compatibility evidence | `docs/project/FEATURE_AND_VALIDATION_MATRIX.md` | Compatibility | `docs/validation/VALIDATION_REGISTER.md` |
| Validation policy and register | `docs/validation/VALIDATION_MAINTENANCE_POLICY.md` | Validation | `docs/validation/VALIDATION_REGISTER.md`, `docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md` |
| Release policy | `docs/release/RELEASE_DOCUMENTATION_POLICY.md` | Release management | `docs/release/RELEASE_CHECKLIST.md`, `CHANGELOG.md` |
| Repository policy | `docs/repository/REPOSITORY_POLICY.md` | Repository maintenance | `docs/repository/REPOSITORY_MAINTENANCE_GUIDE.md`, `docs/repository/GITHUB_REPOSITORY_POLICY.md`, `docs/repository/HACS_PUBLICATION_GUIDE.md`, `docs/repository/RELEASE_PUBLICATION_RUNBOOK.md` |
| Project health dashboard | `docs/project/project_health.json` | Project governance | `docs/project/PROJECT_HEALTH_DASHBOARD.md`, `docs/project/project_health_calculated.json` |
| Continuation package | `handoff/HANDOFF_INDEX.md` | Project continuity | `handoff/28_IMMEDIATE_RESUME_POINT.md`, `handoff/16_RECOVERY_PROMPT.md` |
| Automation assets policy | `docs/automation-assets/AUTOMATION_ASSETS_POLICY.md` | Automation assets | `docs/automation-assets/AUTOMATIONS_GUIDE.md`, `docs/automation-assets/BLUEPRINTS_GUIDE.md`, `docs/automation-assets/LOVELACE_GUIDE.md` |
| Governance automation | `docs/project/GOVERNANCE_AUTOMATION.md` | Project governance | `docs/validation/governance-automation-report.json` |
| Repository rationalization | `docs/project/REPOSITORY_RATIONALIZATION.md` | Repository maintenance | `docs/project/REPOSITORY_DEPENDENCY_MAP.md`, `docs/project/repository_dependency_map.json`, `docs/project/repository_metrics.json` |
| Quality and release intelligence | `docs/quality/evidence_register.json` | Quality and release management | `docs/quality/EVIDENCE_REGISTER.md`, `docs/quality/risk_register.json`, `docs/quality/RISK_REGISTER.md`, `docs/quality/technical_debt_register.json`, `docs/quality/TECHNICAL_DEBT_REGISTER.md`, `docs/quality/decision_traceability.json`, `docs/quality/DECISION_TRACEABILITY.md`, `docs/quality/quality_release_intelligence.json`, `docs/quality/release_decision.json`, `docs/quality/RELEASE_DECISION_REPORT.md`, `docs/quality/QUALITY_RELEASE_INTELLIGENCE.md` |
| Runtime and release certification | `docs/certification/CERTIFICATION_POLICY.md` | Release certification | `docs/certification/BENCHMARK_PROTOCOL.md`, `docs/certification/COMPATIBILITY_CERTIFICATION.md`, `docs/certification/SECURITY_CERTIFICATION.md`, `docs/certification/UX_ACCESSIBILITY_CERTIFICATION.md`, `docs/certification/release_certification.json`, `docs/certification/reports/RELEASE_CERTIFICATION_REPORT.md` |
| Target validation evidence | `docs/target-validation/TARGET_VALIDATION_POLICY.md` | Release certification | `docs/target-validation/TARGET_VALIDATION_GUIDE.md`, `docs/target-validation/target_validation_plan.json`, `docs/target-validation/schema/target_validation_result.schema.json`, `docs/target-validation/runs/README.md` |
| Repository production audit | `docs/production-audit/PRODUCTION_AUDIT_POLICY.md` | Release engineering | `docs/production-audit/README.md`, `docs/production-audit/PRODUCTION_AUDIT_REPORT.md` |
| Home Assistant certification | `docs/home-assistant-certification/HOME_ASSISTANT_CERTIFICATION_POLICY.md` | Release certification | `docs/home-assistant-certification/EXECUTION_RUNBOOK.md`, `docs/home-assistant-certification/CERTIFICATION_STATUS.json` |
| Home Assistant Integration Quality Scale | `docs/quality-scale/QUALITY_SCALE_POLICY.md` | Integration quality | `docs/quality-scale/README.md`, `docs/quality-scale/QUALITY_SCALE_REPORT.md`, `custom_components/btdoor_security_plus/quality_scale.yaml`, `docs/quality-scale/QUALITY_SCALE_WORKFLOW.md`, `docs/quality-scale/quality_scale_workflow.json`, `docs/quality-scale/QUALITY_SCALE_WORKFLOW_STATUS.json`, `docs/quality-scale/QUALITY_SCALE_REMEDIATION_PLAN.md`, `docs/quality-scale/QUALITY_SCALE_REMEDIATION_PLAN.json`, `docs/quality-scale/config_flow_coverage.json`, `tests/test_config_flow_full_coverage.py`, `docs/adr/ADR-0067-quality-scale-bronze-achievement.md`, `handoff/40_QUALITY_SCALE_BRONZE_ACHIEVEMENT.md` |

## Maintenance rules

1. Change the canonical source first.
2. Regenerate or update derived artifacts in the same change.
3. Do not create parallel policy documents for an existing area.
4. Register any replacement path in `deprecated_aliases` until all references are migrated.
5. Run `python tools/repository/analyze_repository.py --check` after structural changes.
