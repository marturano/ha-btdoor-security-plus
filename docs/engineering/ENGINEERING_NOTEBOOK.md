# Engineering Notebook

## 2026-07-21 — 1.1.0-rc.9 documentation reconstruction

### Goal
Create one coherent product history as 1.0 Foundation → 1.1 Core Stable, preserve forensic traceability and identify lost requirements or incomplete implementation.

### Inputs
- 1.1.0-rc.8 source archive;
- active and archived release notes;
- changelog and ADRs;
- tests, entity platforms, services, managers and project manifests;
- RC.8 validation report and continuity handoff.

### Decisions
- Historical 3.x–6.x labels are provenance only.
- Active product documentation begins at reconstructed 1.0 Foundation.
- Exact old archives and ADR acceptance labels are not rewritten.
- Home Assistant compatibility target is 2026.x with evidence levels and exact tested patch versions.
- English is normative for deep engineering documents; user-facing documents remain localized.

### Findings
- Changelog contained duplicate releases, multiple roots and unordered additions.
- Active locale documents contained Alpha.3/6.1 placeholders.
- Compatibility and quality policies referred to obsolete release labels.
- Architecture documentation omitted lifecycle, multi-entry isolation, gate safety and Support Bundle boundaries.
- No active engineering notebook existed.
- ADR-0024 is absent.
- Several retained capabilities were implemented and tested but insufficiently documented: call journal, media diagnostics, sentence management, dashboard resolver, service ownership and registry topology validation.

### Runtime impact
None intended. Version changed only to identify the documentation-governance candidate.

### Follow-up validation
Run source checks, documentation QA, focused regression tests, HACS/hassfest and real Home Assistant lifecycle tests before Stable.

## 2026-07-21 — Complete archive archaeology

### Scope
Audited all 47 files under the removed internal archive, including planning, release and validation evidence.

### Key result
Historical numbering was confirmed to describe one continuous integration. Useful requirements were merged into the 1.0/1.1 model without rewriting the archived evidence.

### Recovered defect
The certificate-expiry blueprint and entity resolver still refer to a certificate days-remaining sensor that is not implemented. This must be implemented or the incomplete feature removed before Stable.

### Other retained obligations
Multi-entry lifecycle symmetry, no-action-on-lifecycle, registry identity preservation, private exports, managed sentence ownership, TLS verification truthfulness and bounded media diagnostics remain explicit release gates.

## Governance and Continuation Package — 2026-07-22

- Consolidated the authoritative workflow, Definition of Ready and Definition of Done.
- Added permanent policies for documented quality reviews, security, benchmarks, translations, automation assets and release publication.
- Rebuilt the Continuation Package contract so a new prompt can resume from repository evidence rather than chat memory.
- The official roadmap content was not modified.

## 2026-07-22 — Documentation consolidation and orphan audit

Reviewed the complete continuation package for duplicate normative documents and orphaned structures. Governance, repository, benchmark, release-policy and validation material was consolidated into canonical locations. Superseded source documents were archived rather than deleted. Deprecated roadmap and handoff entry points were retained only as compatibility pointers. The official roadmap content was not modified.
## 2026-07-22 — Active package cleanup and validation consolidation

Removed the internal archive, deprecated pointers and archive-only audits. Consolidated RC.15 validation evidence under `docs/validation/`, introduced the Validation Maintenance and Update gate, updated canonical tests and added repository orphan/inventory checks.

## 2026-07-22 — Phase 6A Governance Automation

Implemented the first executable governance layer over the existing canonical documents and registers. The framework validates governance structure, handoff continuity, release-readiness structure, repository integrity, repository hygiene and health evidence. It generates separate governed-assessment, automated-health and compliance indicators so that missing or blocked execution cannot be hidden by a manually assigned score.

## 2026-07-22 — Phase 6B Repository Rationalization

- Introduced the canonical-document registry as the governed source-of-truth map.
- Added dependency graph generation, Markdown-link validation, exact duplicate detection and repository metrics.
- Classified unreferenced files conservatively to avoid deleting Home Assistant convention-loaded assets.
- Integrated the rationalization check into governance automation and CI.
- Accepted ADR-0058.

## 2026-07-22 — Phase 6C Quality and Release Intelligence

Implemented structured evidence, risk, technical debt and decision traceability registries. Added automated consistency validation and a release decision engine. The engine intentionally distinguishes tooling success from release approval: the framework can pass while the Final decision remains BLOCKED because required evidence is still missing.

## 2026-07-22 — Phase 6D Runtime and Release Certification

Implemented environment-labelled certification. Repository-local checks are executable; Home Assistant 2026.x, HACS lifecycle and interactive UX evidence remain intentionally pending until run on target infrastructure.

## 2026-07-22 — Phase 6E Target Validation Pack

Implemented portable target evidence collection and immutable import. The framework intentionally leaves Final BLOCKED until a complete Home Assistant 2026.x run is supplied.

## 2026-07-23 — Phase 7C RC Approval assessment

- Read the canonical workflow from `docs/project/WORKFLOW.md` and confirmed Phase 7C as the next approved roadmap activity.
- Executed Quality Scale, Project Impact, Governance, repository validation, health regeneration, Release Readiness and Release Decision checks.
- Confirmed repository-local checks pass and Quality Scale remains Gold.
- Recorded the Release Decision Engine result as BLOCKED by target-runtime, benchmark, UX/accessibility, publication and external Quality Scale evidence.
- Did not start Phase 7D and introduced no runtime change.

## 2026-07-27 — GitHub Sandbox Validation Gate and Ruff remediation path

GitHub Ruff validation exposed a large set of formatting, import and modernisation findings that were not reproduced locally because the execution environment could not retrieve the official Ruff binary. The project adopted ADR-0091: GitHub-hosted validation is now mandatory evidence for every RC and Final release, while local validation remains a prerequisite where available.

Two workflows were introduced. The read-only workflow validates the exact commit and blocks release. The manual remediation workflow installs the latest stable Ruff, applies supported fixes and formatting, runs the complete validation suite, and commits only after success. No lint rule or Quality Scale requirement was relaxed; the GOLD threshold remains mandatory. RC15 remains blocked until the remediation workflow and subsequent read-only workflow both pass on GitHub.

## 2026-07-27 - GitHub validation failure triage

Reviewed the GitHub validation log and identified 882 Ruff findings across 121 files plus an invalid Python/Home Assistant compatibility matrix. Updated the sandbox/remediation workflows and compatibility runtime mapping. Mechanical Ruff remediation is now persisted before semantic residual failures are reported, preventing the previous all-or-nothing workflow from discarding valid safe fixes. Release remains blocked pending a fully green read-only validation run with GOLD retained.

## 2026-07-27 — GitHub Actions effective-validation remediation

### Trigger

GitHub accepted the workflow files after the `runner.temp` correction, but acceptance was incorrectly treated as if repository validation had occurred.

### Findings

- Workflow syntax and workflow execution evidence had been conflated.
- The canonical sandbox runner did not install or execute mypy.
- `pytest-asyncio` was not explicitly installed even though the suite loads its plugin explicitly.
- The main Validate Python job duplicated only part of the canonical sequence.
- No dependency-free contract prevented removal of mandatory workflow jobs or reintroduction of direct shell execution.

### Remediation

- Added `tools/validation/check_github_workflows.py` and regression coverage.
- Expanded the canonical runner to execute Ruff format/lint, mypy, compile, JSON validation, pytest and all repository gates.
- Preserved exit codes through `set -euo pipefail` and a logged-command wrapper.
- Changed `validate.yml` to call the canonical runner and upload evidence even on failure.
- Added a canonical GitHub Actions validation contract and synchronized quality, release, governance and handoff documentation.

### Evidence status

- Workflow contract: locally executed, PASS.
- Bash syntax and Python compilation for the new tooling: locally executed, PASS.
- Individual repository integrity checks: locally executed, PASS.
- Ruff and mypy: NOT VERIFIED locally because the package index returned HTTP 503.
- Full pytest suite: NOT VERIFIED locally; execution progressed through the suite but exceeded the available local command window.
- HACS, Hassfest and GitHub-hosted matrix: NOT VERIFIED until the updated commit is pushed and the remote workflows complete.

The release remains BLOCKED until all mandatory remote jobs are green.
