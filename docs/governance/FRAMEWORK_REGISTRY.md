# Framework Registry

**Status:** Authoritative

| Framework | Responsibility | Primary inputs | Required outputs |
|---|---|---|---|
| Development | Runtime, tests, assets and implementation | Approved scope and design | Source, tests, implementation evidence |
| Validation | Static, unit, integration, regression, repository and target checks | Exact package state | Validation reports and gate results |
| Quality | Quality Scale, coverage, security, performance, UX and accessibility | Validation evidence | Quality reports and certificates |
| Localization | All integration locales and localized user documentation | `strings.json`, translations, language registry | Localization report and completeness status |
| Documentation | Normative and user documentation synchronization | Change classification and DIM | Updated documents, registry and audit report |
| Governance | Rules, ADR, workflow, roadmap constraints and compliance | Proposed policy/process changes | Accepted governance state and traceability |
| Evidence | Evidence, risks, technical debt and decision traceability | Framework outputs | Evidence registry and consolidated status |
| Release | Readiness, decision, package, manifest, inventory, checksums and distribution | Valid certificates and exact package | Readiness certificate, decision and release artifacts |

## Dependency and revalidation rules

- Development changes require Validation review and may propagate to Quality, Evidence and Release.
- Localization changes require Documentation, Evidence and Release review.
- Governance, registry or matrix changes require Governance, Documentation, Evidence and Release revalidation.
- Certificate changes require Evidence and Release revalidation.
- Handoff synchronization is governed jointly by Documentation and Governance.

Impact status uses `NOT_IMPACTED`, `REVIEW_REQUIRED`, `UPDATE_REQUIRED` and `REVALIDATION_REQUIRED` as defined by the Project Impact Analysis Framework.
