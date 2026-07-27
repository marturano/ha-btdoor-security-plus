# Official Development and Release Workflow

**Status:** Authoritative project workflow  
**Applies to:** every feature, fix, refactor, Release Candidate and Final Release  
**Roadmap authority:** only `docs/roadmap/` is canonical. Existing roadmap points must not be silently rewritten, removed or renumbered.

## Mandatory flow

1. Roadmap Alignment
2. Project Scope Review
3. Quality Scale Initial Assessment
4. Quality Scale Target Confirmation
5. Quality Scale Remediation Planning
6. Design Review
7. Definition of Ready Gate
8. Architecture Review
9. Architecture Gate
10. ADR, when required
11. Implementation
12. Quality Scale Safe Remediation Application
13. Engineering Notebook Update
14. Self Review
15. Code Quality Review
16. Static Analysis and Linting
17. Unit Tests
18. Integration Tests
19. Regression Tests
20. Test Quality Review
21. Quality Gate
22. Security Review, when applicable
23. Security Documentation Review and Update
24. Security Gate
25. Performance Review, when applicable
26. Benchmark Review and Update
27. Performance Gate
28. UX Review
29. Accessibility Review
30. Translation Verification
31. Translation Review and Update
32. Compatibility Verification
33. Compatibility Matrix Review and Update
34. Documentation Review
35. Project Documentation Review and Update
36. Automation Assets Review and Update
37. Documentation Gate
38. Quality Scale Final Assessment
39. Quality Scale Remediation Verification
40. Quality Scale Gate
41. Validation Maintenance and Update
42. Validation Gate
43. Quality Review Documentation and Update
44. CHANGELOG Review and Update
45. Release Documentation Review and Update
46. Repository Documentation Review and Update
47. Repository Rationalization and Canonical Reference Check
48. QA
49. Project Health Dashboard Update
50. Release Readiness Gate
51. Publication Readiness
52. Publication Gate
53. Handoff Review and Update
54. Release Candidate Validation, or HACS and GitHub Publication Validation for Final Releases
55. Final Release Gate, for Final Releases
56. Release
57. Post Release Review
58. Engineering Notebook Closure
59. Lessons Learned and Continuous Improvement
60. Project Health Dashboard Closure Update

## Gate model

The workflow distinguishes **activities**, which produce or update project artifacts, from **gates**, which are formal decisions supported by versioned evidence. Gate definitions, entry criteria, exit criteria and blocking conditions are maintained in `docs/project/WORKFLOW_GATES.md`.

A review or gate that is not documented is considered not performed. No downstream gate may override an unresolved upstream blocker without an explicit, accepted exception recorded in the Decision Log.

## Project Health Dashboard rule

The Project Health Dashboard is a mandatory governed artifact. It must be regenerated after Validation Maintenance and Update, before Release Readiness, after any gate-status change, and at release closure. Its data source is `docs/project/project_health.json`; its rendered view is `docs/project/PROJECT_HEALTH_DASHBOARD.md`.

The dashboard summarizes evidence but never replaces the underlying review, register, report or gate decision.

## Static-analysis rule

Static analysis and linting must include all applicable Python, YAML, JSON, manifest, translation and Home Assistant checks defined by repository tooling. Missing tooling must be documented as a gap rather than silently treated as passed.

## Test-layer rule

Unit, integration and regression testing are distinct activities. A release report must state which layers were executed, which were not applicable and which remain blocked by runtime or environment requirements.

## Transversal documentation rule

“Project Documentation Review and Update” means the whole documentation ecosystem: user, developer, API, architecture, governance, compatibility, translations, automation assets, release, QA, security, repository operations, ADR, Decision Log, Engineering Notebook, Project Health Dashboard and Handoff.

## Automation-assets rule

When a release implements or changes automations, blueprints, Lovelace dashboards, scripts, templates, packages, AI integrations or examples, official assets and usage guides must be created or updated in the same release.

## Validation-maintenance rule

After documentation review and before release-readiness assessment, all affected checks must be rerun and their evidence consolidated into `docs/validation/`. The validation register, current release report, Project Health Dashboard, handoff and release documentation must match the exact package state. Obsolete or duplicated evidence must not remain in parallel locations.

## Final-release publication rule

Every Final Release must validate the complete GitHub and HACS lifecycle and include maintained instructions for upload, publication, synchronization, installation, upgrade, rollback and online repository maintenance.

## Repository-rationalization rule

Repository Documentation Review must be followed by the canonical-reference and dependency analysis. The canonical registry, dependency map and repository metrics must match the exact package state. Unreferenced files are review candidates, not automatic deletion targets; convention-loaded runtime assets require explicit impact evidence before removal.

## Quality and Release Intelligence maintenance

Before Release Readiness, update the Evidence Register, Risk Register, Technical Debt Register and Decision Traceability, then generate the Release Decision Report. A BLOCKED report is authoritative and cannot be overridden by the aggregate Project Health score.

## Runtime and release certification rule

Before Release Readiness, execute repository-local certification. Before Final Release, execute Home Assistant target-runtime and publication certification. Local evidence must never be represented as target-runtime evidence.

## Quality Scale workflow rule

Every phase starts and ends with a Home Assistant Integration Quality Scale assessment. Gold is the fixed release minimum, desired tier and maximum governed tier. `python tools/quality_scale/quality_scale_workflow.py check` must pass before advancement. Any regression below Gold blocks the workflow. Platinum is informational and out of scope unless a new explicit ADR reopens it. Canonical artifacts are maintained in `docs/quality-scale/`.
## Governance completion rules

The workflow is governed by `docs/governance/GOVERNANCE_RULE_REGISTRY.md`. RG-001 through RG-004 are mandatory. The Document Impact Matrix determines all documents and evidence affected by a change; the Workflow Compliance Matrix determines mandatory frameworks, rules and certificates.

## Documentation synchronization rule

Documentation synchronization is an executable workflow stage, not a final editorial review. A phase cannot close until all impacted normative documents, registries, matrices, localized user documents, generated evidence, release documents and handoff status are synchronized with the exact package. Handoff documents may report state and link to canonical sources but must not duplicate normative content.

## Localization framework rule

Translation Verification and Translation Review apply to every locale declared in `docs/i18n/language_registry.json`. The base key schema is `strings.json`; all shipped locale files must maintain key and placeholder parity. The six localized documentation locales remain governed by `docs/document_manifest.yaml`. RG-003 failure blocks completion and release approval.

## Phase 7C and 7D transition

Phase 7C executes all mandatory gates, synchronizes evidence and risk registers, emits the exact-package Release Readiness Certificate and permits the Release Decision Engine to return `APPROVED` only when RG-001 through RG-004 pass. Phase 7D begins only after that approval and performs GitHub/HACS packaging, definitive release notes, release manifest, checksums, final inventory and production of `1.1.0 Final`.


## Project Impact Analysis and automatic handoff synchronization

Before implementation, every change must execute the Project Impact Analysis Framework defined in `docs/governance/PROJECT_IMPACT_ANALYSIS_FRAMEWORK.md`. The analysis covers runtime, documents, frameworks, registries, matrices, certificates, localization, evidence, release and handoff domains. Framework dependencies may expand, but never reduce, the required work.

After implementation and before evidence consolidation, every impacted framework must be revalidated. Documentation synchronization is followed by automatic handoff synchronization. The handoff gate verifies `HANDOFF_INDEX.md`, current project state, build information, resume point and the numbered iteration handoff against the exact package.

The operational sequence is therefore:

1. Bootstrap
2. Repository Audit
3. Gap Analysis
4. Project Impact Analysis
5. Implementation
6. Framework Revalidation
7. Validation
8. Repository Hygiene
9. Documentation Synchronization
10. Automatic Handoff Synchronization
11. Evidence Generation
12. Decision Engine
13. Package Generation
14. Release

This sequence refines the detailed mandatory flow without changing approved roadmap phase order.
