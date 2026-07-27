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
