# Governance Rule Registry

**Status:** Authoritative

This registry is the single source of truth for mandatory project-governance rules.

## Core rules

### CR-001 — Bootstrap Required
No activity may start before the mandatory bootstrap set and canonical master documents have been reviewed.

### CR-002 — Single Source of Truth
Every normative fact must have one authoritative source. Summaries may link to it but may not maintain competing policy text.

### CR-003 — Real Implementation
No implementation, validation, certificate or release claim may be made unless it exists in the exact repository state and is supported by evidence.

### CR-004 — Evidence First
Every completion or approval claim must be backed by reproducible evidence tied to the exact package.

### CR-005 — Layer Separation
Runtime, tooling, documentation, governance, evidence and release artifacts must remain explicitly separated and traceable.

## Governance rules

### RG-001 — Final Release Approval
A Release Candidate may be promoted to Final only when all mandatory gates pass, the Release Decision Engine returns `APPROVED`, Home Assistant Quality Scale is verified at `GOLD`, no unaccepted blocking risk remains, and the Release Readiness Certificate is valid for the exact package.

### RG-002 — Documentation Completeness
A phase or change may not be declared complete until every impacted normative document, registry, matrix, generated evidence set, release document and handoff status has been updated and verified against the exact repository state.

### RG-003 — Localization Completeness
Any change that adds, modifies or removes localizable content must update every integration locale declared in the Language Registry. Key parity, placeholders, JSON validity, non-empty values and applicable localized user documentation must pass before completion.

### RG-004 — Single Source of Truth
Normative information may have only one authoritative source. Other documents may summarize status or link to the source, but must not maintain competing copies of workflows, policies, rules, roadmaps or release decisions.

### RG-005 — Repository Hygiene
Every iteration must check unused files, empty directories, temporary artifacts, duplicate documents and obsolete generated outputs. Candidates are archived or explicitly retained; convention-loaded runtime assets are never removed without impact evidence.

### RG-006 — Automatic Handoff Synchronization
Every completed iteration must synchronize the handoff index, current project state, build information, resume point and a numbered iteration handoff. Handoff synchronization is a blocking gate.

### RG-007 — Framework Consistency
Every change must identify impacted frameworks and complete every required update or revalidation before closure.

### RG-008 — Registry Consistency
Every impacted registry must be updated and validated against the exact repository state.

### RG-009 — Matrix Consistency
Impact, compliance and dependency matrices must remain synchronized with workflow, rules, frameworks, registries and validators.

### RG-010 — Certificate Consistency
A change invalidates every affected certificate. Invalidated certificates must be regenerated for the exact package before they may support a gate or decision.

### RG-011 — Framework First
Before implementation, the project must determine impacted frameworks, registries, matrices, certificates, evidence and handoffs through the Project Impact Analysis Framework.

## Workflow rules

- **WR-001:** Every phase begins with gap analysis.
- **WR-002:** Every implementation is preceded by project impact analysis.
- **WR-003:** Every implementation is followed by framework revalidation.
- **WR-004:** Repository hygiene is mandatory before package generation.
- **WR-005:** Operational handoffs are generated or synchronized automatically and validated before closure.

## Impact rules

- **IR-001:** Every change evaluates all ten PIAF domains.
- **IR-002:** Every detected impact produces a deterministic artifact and validation action list.
- **IR-003:** No `UPDATE_REQUIRED` or `REVALIDATION_REQUIRED` item may remain incomplete at phase closure.

## Validation rules

- **VR-001:** Every validator must be independently executable.
- **VR-002:** Validators return `PASS`, `WARNING` or `FAIL`, with `FAIL` blocking and warnings explicitly adjudicated.
- **VR-003:** Validator results used by release governance must be consumable by the Governance Orchestrator and Decision Engine.

## Release rules

- **RR-001:** A Release Candidate cannot become Final without Decision Engine `APPROVED`.
- **RR-002:** Official packages are generated reproducibly from the validated repository state.
- **RR-003:** Every official package includes an automatically calculated SHA256 checksum.
- **RR-004:** Superseded package artifacts are archived according to repository policy.

## Meta-governance rule

### MGR-001 — Governance Evolution
Any change to governance, workflow, frameworks, matrices, registries, rules, validators or certificates must undergo the same bootstrap, impact analysis, synchronization, validation and evidence requirements imposed on runtime work.

## Enforcement

The canonical workflow, Project Impact Analysis Framework, Document Impact Matrix and Workflow Compliance Matrix determine when each rule applies. Exceptions require an accepted ADR and must be represented in evidence, risk and decision traceability records.

### GR-GITHUB-SANDBOX-001 — Mandatory latest-Ruff release validation
- **Scope:** every RC and Final release.
- **Requirement:** validate the exact release commit in a clean GitHub-hosted sandbox with Python 3.13, latest stable official Ruff and every mandatory repository validator.
- **Failure handling:** correct all errors and rerun the complete suite.
- **Forbidden workarounds:** disabling checks, broad ignores, lowering Quality Scale or accepting incomplete evidence.
- **Minimum Quality Scale:** GOLD until explicitly changed through governance.
- **Evidence:** Python/Ruff versions, lint, test, publication, integrity, documentation, hygiene, governance and certification reports.
