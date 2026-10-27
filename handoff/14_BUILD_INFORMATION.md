# Build Information

## Current Linux validation checkpoint — 2026-10-27

Ruff/format, mypy, 347 pytest tests, fresh coverage 95.01%, all 18 governance subchecks, publication, integrity, hygiene and the canonical runner PASS on Ubuntu/Python 3.14.2. Real HA 2026.7.2 import/API smoke PASS. Historical local failures below are superseded for this code. Remote commit checks and live target certification remain separate; Final remains BLOCKED.

See [the Linux validation report](../docs/validation/LINUX_VALIDATION_2026-10-27.md).


## Current Ruff checkpoint — 2026-10-27

Ruff: 77 to 0; format check passes. Windows/Python 3.12 pytest: 337 passed, 3 existing failures reproduced on the original ZIP. mypy executed and failed (160 diagnostics, including missing Home Assistant imports). Fresh coverage, Linux CI, remote checks and live HA/SIP/Cloud remain unverified. Final remains BLOCKED. Historical full-pass and coverage claims do not validate this edited package.

See [the current validation report](../docs/validation/RUFF_RESIDUAL_REMEDIATION_2026-10-27.md).

**Status:** Current operational snapshot  
**Normative:** No — generated evidence and master documents prevail

- Version: `1.1.0-rc.15`
- Current package: `1.1.0-rc.15-phase7c-github-publication-ready`
- Build type: Phase 7C target-validation readiness
- Runtime delta: binary DER/PKCS#7 certificate parsing now preserves payload bytes; target-validation run identity is filesystem-safe
- DRP: 2.0
- PCP: 2.0
- Canonical roadmap: `docs/roadmap/ROADMAP.md`
- Canonical workflow: `docs/project/WORKFLOW.md`
- Validation report: `docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md`
- Repository inventory: `docs/project/REPOSITORY_INVENTORY.md`
- Project Health Dashboard: `docs/project/PROJECT_HEALTH_DASHBOARD.md`

## Current governed state

- Quality Scale: GOLD / PASS
- Maximum and desired governed tier: GOLD
- Platinum: historical/informational only; outside active scope
- Localization framework: 17 runtime locales; 6 full-documentation locales
- Repository hygiene: PASS
- Documentation consistency: PASS after consolidation
- Release Readiness Certificate: PASS for package-level checks only
- Release Decision Engine: BLOCKED pending exact-package target and external evidence
- Final release approval: not granted

## Package lineage

1. `1.1.0-rc.15-quality-release-intelligence` — Phase 6C historical baseline.
2. `1.1.0-rc.15-runtime-release-certification` — Phase 6D historical lineage.
3. `1.1.0-rc.15-target-validation-pack` — Phase 6E historical lineage.
4. `1.1.0-rc.15-governance-consolidation` — governance consolidation lineage.
5. `1.1.0-rc.15-pre-phase7c-audited` — repository bootstrap and hygiene lineage.
6. `1.1.0-rc.15-project-impact-governance` — governance baseline.
7. `1.1.0-rc.15-phase7c-assessment` — Phase 7C assessment lineage.
8. `1.1.0-rc.15-phase7c-cold-audit` — cold repository audit package.
9. `1.1.0-rc.15-phase7c-runtime-hardening` — runtime lifecycle hardening package.
10. `1.1.0-rc.15-phase7c-local-certification` — repository-local certification package.
11. `1.1.0-rc.15-phase7c-github-publication-ready` — current target-validation readiness package.

Historical test counts remain evidence of their respective packages and must not be interpreted as the current suite result. Current validation results are recorded by the exact-package validation reports and generated certificates.

## Governance tooling

The exact package includes `project_impact` and `handoff_synchronization` blocking gates in Repository Integrity and the Governance Orchestrator.

12. `1.1.0-rc.15-phase7c-github-publication-ready` — corrected target contract: supported 2026.x series, 2026.7.x reference target.

13. `1.1.0-rc.15-phase7c-github-publication-ready` — target-validation run identity and filesystem-boundary hardening.

## Release Candidate Dossier

The authoritative Phase 7C dossier is `docs/release/RELEASE_CANDIDATE_DOSSIER.md`; decision remains BLOCKED.
