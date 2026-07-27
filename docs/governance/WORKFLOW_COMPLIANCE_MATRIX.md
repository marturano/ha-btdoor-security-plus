# Workflow Compliance Matrix

**Status:** Authoritative operational matrix

| Change type | Mandatory frameworks | Mandatory rules | Minimum gates/certificates |
|---|---|---|---|
| Bug fix | Development, Validation, Documentation, Evidence | RG-002, RG-004 | Tests, documentation completeness |
| New feature | Development, Validation, Quality, Localization, Documentation, Evidence | RG-002, RG-003, RG-004 | Quality, localization, documentation, validation |
| Runtime/API change | Development, Validation, Quality, Localization, Documentation, Governance, Evidence | RG-002, RG-003, RG-004 | Architecture, compatibility, localization, regression |
| Policy/gate/framework change | Governance, Documentation, Validation, Evidence | RG-002, RG-004 | Governance and documentation completeness |
| Translation-only change | Localization, Validation, Documentation, Evidence | RG-002, RG-003, RG-004 | Localization completeness |
| Release Candidate | All applicable frameworks | RG-002, RG-003, RG-004 | All RC gates and exact-package evidence |
| Final Release | All frameworks | RG-001, RG-002, RG-003, RG-004 | Gold, readiness certificate, APPROVED decision, publication validation |
