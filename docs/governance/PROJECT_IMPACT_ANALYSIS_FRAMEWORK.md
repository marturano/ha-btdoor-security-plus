# Project Impact Analysis Framework

**Status:** Authoritative

The Project Impact Analysis Framework (PIAF) is the mandatory pre-implementation and post-implementation control for every repository change. It extends, but does not replace, the Document Impact Matrix.

## Impact domains

Every change must be classified against all of the following domains:

1. Runtime
2. Documents
3. Frameworks
4. Registries
5. Matrices
6. Certificates
7. Localization
8. Evidence
9. Release
10. Handoff

Each domain receives one status:

- `NOT_IMPACTED`
- `REVIEW_REQUIRED`
- `UPDATE_REQUIRED`
- `REVALIDATION_REQUIRED`

`UPDATE_REQUIRED` and `REVALIDATION_REQUIRED` are blocking until the corresponding artifacts and checks are complete.

## Framework impact model

The Framework Impact Matrix is embedded in the Document Impact Matrix and covers Development, Validation, Quality, Localization, Documentation, Governance, Evidence and Release. Framework dependencies propagate impact downstream:

- Development → Validation → Quality → Evidence → Release
- Localization → Documentation → Evidence → Release
- Governance → Documentation → Evidence → Release
- Registry or matrix changes → Governance, Documentation, Evidence and Release
- Certificate changes → Evidence and Release
- Handoff changes → Documentation and Governance validation

A dependency may increase impact severity but may never reduce it.

## Handoff Impact Controller

Every completed change must synchronize the operational handoff set:

- `handoff/HANDOFF_INDEX.md`
- `handoff/03_PROJECT_STATE.md`
- `handoff/14_BUILD_INFORMATION.md`
- `handoff/28_IMMEDIATE_RESUME_POINT.md`
- one numbered iteration handoff

The controller must verify package identity, current phase, Decision Engine state, Quality Scale state, validation results, changed-file evidence and the next resume point. Historical handoffs remain immutable except for classification metadata or corrected canonical references.

## Completion contract

A change is complete only when:

1. impact analysis exists;
2. every required update is present;
3. every required revalidation passes;
4. generated evidence matches the exact repository state;
5. handoff synchronization passes;
6. no framework, registry, matrix, certificate or release dependency remains stale.

## Meta-governance

Governance artifacts are governed artifacts. Any change to rules, workflow, frameworks, registries, matrices, validators or certificates must itself pass bootstrap, impact analysis, synchronization, validation and evidence generation.
