# Documentation Consolidation Audit

**Package audited:** 1.1.0-rc.15 QS-23 Gold Project Policy  
**Outcome:** Architecture consolidated; historical evidence retained; normative duplication reduced.

## Inventory findings

- The repository contains more than four hundred Markdown documents, primarily historical phase evidence, localized user documentation and generated reports.
- Normative workflow content was duplicated verbatim in `docs/project/WORKFLOW.md` and `handoff/24_OFFICIAL_WORKFLOW.md`.
- Release-decision logic, evidence and risk registers already existed, but their relationship to documentation and localization completeness was not expressed by one governance architecture.
- Runtime translations include seventeen locales, while the previous translation QA validated only six. This was a material governance gap.
- Handoff files mixed current state, historical evidence and duplicated policy text.

## Consolidation decisions

1. `docs/project/WORKFLOW.md` remains the only authoritative workflow.
2. Handoff documents become state/evidence pointers and must not copy normative text.
3. Historical phase and Quality Scale evidence is retained because it is traceability, not redundant policy.
4. The Project Governance System, framework registry, rule registry and two operational matrices become canonical governance sources.
5. Localization completeness now covers every shipped integration locale; localized documentation remains required for the six declared documentation locales.
6. Generated reports remain generated artifacts and do not become normative sources.

## Items intentionally not deleted

Historical ADR, validation, Quality Scale and handoff evidence was preserved because removal would break traceability. Future cleanup may archive superseded evidence only after reference and release-history validation.
