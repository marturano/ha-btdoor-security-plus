# Document and Project Impact Matrix

**Status:** Authoritative operational matrix

This matrix is the canonical Document Impact Matrix and the operational entry point for the Project Impact Analysis Framework.

`M` = mandatory update, `C` = conditional review/update, `R` = regenerate/revalidate, `—` = normally not impacted.

## Artifact impact

| Change type | Roadmap | Workflow / rules | Architecture / developer | User docs / README | Localization | Validation / evidence | Changelog / release notes | Handoff |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Bug fix | C | — | C | C | C | M | M | M |
| New feature | M | C | M | M | M | M | M | M |
| Runtime/API behavior change | C | C | M | M | M | M | M | M |
| Refactor without behavior change | — | C | M | — | — | M | C | M |
| Security change | C | C | M | C | C | M | M | M |
| New or changed policy/gate/framework | C | M | C | — | C | M | M | M |
| Translation-only change | — | — | — | C | M | M | C | M |
| Documentation-only change | C | C | C | C | C | R | C | M |
| Release Candidate | M | R | R | R | R | M | M | M |
| Final Release | M | R | R | M | R | M | M | M |

## Framework Impact Matrix

| Change type | Development | Validation | Quality | Localization | Documentation | Governance | Evidence | Release |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Bug fix | M | R | C | C | C | C | R | C |
| New feature | M | R | R | M | M | C | R | C |
| Runtime/API behavior change | M | R | R | M | M | C | R | C |
| Refactor without behavior change | M | R | C | — | C | C | R | C |
| Security change | M | R | R | C | M | R | R | R |
| New or changed policy/gate/framework | C | R | C | C | M | M | R | R |
| Translation-only change | — | R | C | M | M | C | R | C |
| Documentation-only change | — | R | C | C | M | R | R | C |
| Release Candidate | R | R | R | R | R | R | R | M |
| Final Release | R | R | R | R | R | R | R | M |

## Additional impact domains

Every row also requires explicit review of registries, matrices, certificates, release state and handoff state. A governance, framework, registry, matrix, certificate or validator change automatically triggers MGR-001 and cannot be treated as documentation-only.

## Mandatory interpretation

- `Localization` means every locale in `docs/i18n/language_registry.json`, not a selected subset.
- `Validation / evidence` includes evidence, risk and decision traceability updates where applicable.
- `Handoff` synchronization includes the index, current state, build information, resume point and one numbered iteration handoff.
- `R` invalidates prior evidence until exact-package revalidation succeeds.
- The matrix is a minimum. Dependency propagation defined by PIAF may only expand the impact set.

## Phase 7C — GitHub Sandbox Validation Gate

| Artifact | Impact | Action |
|---|---|---|
| ADR registry | New permanent architectural/governance decision | Added ADR-0091 |
| Quality gates | New blocking RC/Final gate | Updated |
| Governance system and registry | New permanent rule | Updated |
| GitHub workflows | New validation and remediation workflows | Added |
| Validation tooling | Canonical sandbox runner and evidence output | Added |
| Engineering notebook | Decision and implementation trace | Updated |
| Handoff memory/status | Continuity and resume instructions | Updated |
| CHANGELOG | Governance, CI and documentation changes | Updated |
| Quality Scale policy | GOLD threshold preserved; downgrade prohibited | Confirmed |

## GitHub validation pipeline change impact

| Impact domain | Required action |
|---|---|
| Workflow files | Re-run workflow contract and every modified workflow |
| Validation runner | Re-run Ruff, mypy, pytest, publication, integrity, hygiene, governance and certification |
| Test dependencies | Record exact versions in validation evidence |
| Release documentation | Update checklist, changelog and evidence status |
| Handoff | Record verified, failed and unverified gates without inference |
| Packaging | Invalidate all earlier package checksums and regenerate from the validated tree |


## Ruff residual remediation — 2026-10-27

Runtime: revalidate certificate path dispatch; SIP/Cloud contracts retained. Test/tool cleanup: local revalidation recorded. Documentation/handoff: updated. Localization, schemas, versions, ADR policy and release decisions: unchanged. Coverage, Linux CI, typing and target certification: exact-package revalidation required; historical evidence is not promoted.


## Linux validation completion — 2026-10-27

Runtime: internal typing, guards and SIP/Cloud contracts preserved and regression-tested. Development/validation: pinned dependencies, isolated runner, delegated publication and smoke-import corrections revalidated. Documentation/evidence/handoff: updated. Localization, public schemas, versions, Gold threshold and release rules: unchanged. Linux local certificates refreshed; remote and live-target certificates remain required.
