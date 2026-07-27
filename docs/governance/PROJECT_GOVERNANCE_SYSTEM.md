# Project Governance System

**Status:** Authoritative architecture

The Project Governance System governs the complete repository lifecycle. It does not replace the official roadmap; it defines how roadmap work is executed, documented, evidenced, certified and released.

## Canonical layers

1. **Lifecycle:** roadmap alignment, implementation, verification, certification, release and post-release review.
2. **Frameworks:** Development, Validation, Quality, Localization, Documentation, Governance, Evidence and Release.
3. **Registries:** governance rules, frameworks, languages, evidence, risks and canonical documents.
4. **Matrices:** document impact and workflow compliance.
5. **Generated evidence:** reports, certificates, manifests, inventories and checksums.
6. **Decision:** Release Readiness Certificate followed by the Release Decision Engine.

## Authority order

1. `docs/roadmap/` — committed scope and phase order.
2. `docs/project/WORKFLOW.md` — mandatory execution sequence.
3. `docs/governance/GOVERNANCE_RULE_REGISTRY.md` — mandatory governance rules.
4. `docs/governance/FRAMEWORK_REGISTRY.md` — framework responsibilities.
5. `docs/governance/DOCUMENT_IMPACT_MATRIX.md` and `WORKFLOW_COMPLIANCE_MATRIX.md` — deterministic impact and compliance mapping.
6. Generated reports and handoff documents — evidence and current state only.

## Completion model

A change is complete only when implementation, required validation, evidence generation, localization synchronization, documentation synchronization, governance synchronization and release synchronization have all completed as required by the matrices.

## Project Impact Analysis layer

The Project Impact Analysis Framework is mandatory before implementation and is governed by `docs/governance/PROJECT_IMPACT_ANALYSIS_FRAMEWORK.md`. It evaluates runtime, document, framework, registry, matrix, certificate, localization, evidence, release and handoff impact. Its Framework Impact Matrix extends the Document Impact Matrix and its dependency rules propagate required revalidation.

## Automatic handoff control

Handoff is a generated operational view, not a normative authority. Every completed iteration must synchronize the handoff index, current state, build information, resume point and numbered iteration record. The `handoff_synchronization` gate blocks package generation when those artifacts are missing, stale or inconsistent.

## Permanent GitHub validation rule

The release governance system includes the GitHub Sandbox Validation Gate defined by ADR-0091. Every RC and Final release decision requires evidence from a clean GitHub-hosted sandbox running the latest stable official Ruff release and the complete validation toolchain. Any error blocks release and must be corrected. Validation configuration may not be weakened and the required Home Assistant Integration Quality Scale level may not be reduced as a workaround.
