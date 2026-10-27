# Project State

## Current Linux validation checkpoint — 2026-10-27

Ruff/format, mypy, 347 pytest tests, fresh coverage 95.01%, all 18 governance subchecks, publication, integrity, hygiene and the canonical runner PASS on Ubuntu/Python 3.14.2. Real HA 2026.7.2 import/API smoke PASS. Historical local failures below are superseded for this code. Remote commit checks and live target certification remain separate; Final remains BLOCKED.

See [the Linux validation report](../docs/validation/LINUX_VALIDATION_2026-10-27.md).


## Current Ruff checkpoint — 2026-10-27

Ruff: 77 to 0; format check passes. Windows/Python 3.12 pytest: 337 passed, 3 existing failures reproduced on the original ZIP. mypy executed and failed (160 diagnostics, including missing Home Assistant imports). Fresh coverage, Linux CI, remote checks and live HA/SIP/Cloud remain unverified. Final remains BLOCKED. Historical full-pass and coverage claims do not validate this edited package.

See [the current validation report](../docs/validation/RUFF_RESIDUAL_REMEDIATION_2026-10-27.md).

**Status:** Current operational handoff  
**Normative:** No — master documents prevail  
**Current package:** `1.1.0-rc.15-phase7c-github-publication-ready`

- Current product milestone: 1.1.0 RC15 release-candidate approval preparation.
- Current official phase: Phase 7C — Release Candidate Approval is active and blocked by target/external evidence.
- Runtime focus: native gate button, optional Alexa/Google voice bridge, config-entry isolation, diagnostics and support safety.
- Quality Scale: GOLD, permanent governed maximum; Platinum is not part of the active roadmap.
- Release Readiness Certificate: PASS for package-level readiness checks only.
- Release Decision Engine: BLOCKED pending exact-package external and target evidence; no Final approval is granted.
- Canonical roadmap: `docs/roadmap/ROADMAP.md`.
- Canonical workflow: `docs/project/WORKFLOW.md`.

## Current continuation build

`1.1.0-rc.15-phase7c-github-publication-ready` is the current package source of truth. Repository-local certification passes with 332/332 tests. The Target Validation Pack is now field-ready for Home Assistant 2026.x, with 2026.7.x as the reference target; static analysis and external validators remain pending in CI. The official gate workflow, generated Project Health Dashboard, localization framework and explainable Release Decision Engine are active.

## Governance evolution

The Project Impact Analysis Framework, Framework Impact Matrix, expanded project-rule registry and automatic handoff synchronization gate are active. They are governance-only changes and do not alter the approved roadmap: the next official phase remains Phase 7C RC Approval.

## Phase 7C current state

Phase 7C — Release Candidate Approval is active. Repository-local gates pass and Gold is preserved, but exact-package Final approval remains BLOCKED pending target-runtime, performance, UX/accessibility, publication and external Quality Scale evidence. Phase 7D is not authorized.

## Latest Phase 7C delta

The target-validation field kit now enforces safe run identifiers and result/directory identity consistency. This is tooling hardening only; Phase 7C remains blocked pending external target evidence.

## Release Candidate Dossier

The authoritative Phase 7C dossier is `docs/release/RELEASE_CANDIDATE_DOSSIER.md`; decision remains BLOCKED.
