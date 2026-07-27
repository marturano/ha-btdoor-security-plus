# BTDoor Security+ Project Constitution

## Purpose

This constitution defines the permanent governance rules of BTDoor Security+. It has precedence over informal notes and chat history.

## Permanent principles

- `docs/roadmap/` is the sole authoritative roadmap.
- Existing approved roadmap points are immutable unless a new explicit decision records the change.
- The repository must remain releasable, traceable and recoverable.
- Documentation has the same completion weight as code.
- Every review must produce versioned evidence.
- Every handoff is a complete replacement and must be self-contained.
- ADRs record architectural decisions; the Decision Log records operational decisions; the Engineering Notebook records the technical journey.
- Project status may never claim work that was not actually executed and evidenced.
- Every modification must leave the project in a better state than it found it.

## Mandatory governed artifacts

- Workflow, Definition of Ready and Definition of Done
- Engineering Notebook
- Quality Review Register and release quality dossiers
- Security Policy and security reviews
- Benchmark policy, baselines and reports
- Translation Review
- Compatibility Matrix
- Automation, blueprint and Lovelace guides when applicable
- CHANGELOG and per-release documentation
- HACS and GitHub publication validation for every Final Release
- Complete Continuation Package in `handoff/`
- Project Health Dashboard, structured source and reproducible renderer

## Completion law

No modification or release is complete until all applicable workflow gates pass and their evidence is committed with the code.

## Governance roles

### Project Maintainer

The maintainer preserves the canonical roadmap and architecture foundation, accepts governance and release decisions, approves deprecations and migrations, and ensures the Continuation Package remains complete.

### Reviewer

A reviewer verifies roadmap scope, architectural alignment, tests, documentation, migration evidence, security, privacy and compatibility. Missing mandatory evidence is release-blocking.

### Contributor

A contributor preserves stable identifiers, adds proportionate tests, updates affected canonical documents and raises an ADR when a change crosses an architectural or public-contract boundary.

## Decision process

Routine changes may follow normal review when they remain inside an approved milestone, preserve public contracts and include required tests and documentation. An ADR is mandatory for changes to module boundaries, runtime ownership, persistence, identity, public entities/actions/events/APIs, security/privacy policy, compatibility policy, external providers or documentation source-of-truth rules.

## Decision precedence

1. Project Execution Contract.
2. Project Constitution and accepted ADRs.
3. Architecture Foundation and official roadmap, each within its governed scope.
4. Specialist policies.
5. Generated reports and historical evidence.

Generated evidence never overrides a normative project rule.


## Validation maintenance

Validation is a maintained project asset. Every applicable change must update the canonical validation report and register after QA and before Release Readiness. Fragmented, obsolete, duplicated or unreferenced validation evidence must be consolidated or removed after preserving unique information.

## Project health governance

Project health is evidence-based. The dashboard must reflect the canonical registers and reports, expose blockers without dilution, and be regenerated after validation maintenance, before release readiness, after gate decisions and at release closure. Dashboard scores never override mandatory gate criteria.
