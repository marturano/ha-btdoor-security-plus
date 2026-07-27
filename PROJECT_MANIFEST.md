# BTDoor Platform Project Manifest

| Field | Value |
|---|---|
| Repository | `ha-btdoor-security-plus` |
| Umbrella platform | BTDoor Platform |
| Active product | BTDoor Security+ |
| Current release | `1.1.0-rc.15` |
| Current package | `1.1.0-rc.15-phase7c-github-publication-ready` |
| Phase | Phase 7C — Release Candidate Approval (cold audit complete; blocked) |
| Home Assistant target | 2026.x; primary validation 2026.7.x |
| Documentation model | DRP 2.0 |
| Continuity package | PCP 2.0 |
| Source of truth | Repository |

## Canonical entry points

1. [`handoff/00_PROJECT_EXECUTION_CONTRACT.md`](handoff/00_PROJECT_EXECUTION_CONTRACT.md)
2. [`handoff/01_PROJECT_MEMORY.md`](handoff/01_PROJECT_MEMORY.md)
3. [`handoff/HANDOFF_INDEX.md`](handoff/HANDOFF_INDEX.md)
4. [`docs/index.md`](docs/index.md)
5. [`docs/FOUNDATION.md`](docs/FOUNDATION.md)
6. [`docs/roadmap/ROADMAP.md`](docs/roadmap/ROADMAP.md)
7. [`docs/release/RELEASE_CHECKLIST.md`](docs/release/RELEASE_CHECKLIST.md)
8. [`docs/validation/VALIDATION_REGISTER.md`](docs/validation/VALIDATION_REGISTER.md)

## Document lifecycle

- **Active:** normative and current.
- **Generated:** produced by validation or release tooling.
- **Deprecated:** retained temporarily as a compatibility pointer.

No critical project decision may exist only in a conversation.


## RC15 additions
- [Project Governance](docs/project/PROJECT_CONSTITUTION.md)
- Repository Integrity Suite
- Roadmap Integrity Check


## RC.15 Phase 2 architecture foundation

Canonical entry point: `docs/architecture/README.md`. The Repository Integrity Suite now includes blocking `architecture` and `mermaid` gates. Entry runtime ownership is formalized by ADR-0047.

## RC.15 Phase 3 ecosystem foundation

Canonical entry point: `docs/ecosystem/README.md`. The support matrix is normative and the Repository Integrity Suite includes the blocking `ecosystem` gate.


## RC.15 Phase 4 AI platform foundation

Canonical entry point: `docs/ai/README.md`. Provider independence, policy-first dispatch and local-first privacy are formalized by ADR-0050 through ADR-0053. RIS includes blocking `ai_documentation` and `provider_capability` gates.

## RC.15 Phase 5 API foundation

Canonical entry point: `docs/api/README.md`. Public entity, action, event, error, versioning, security and voice-assistant contracts are now normative. RIS includes strengthened `api` and new `voice_assistant_api` gates. ADR-0054 through ADR-0056 govern public surfaces, physical target isolation and assistant exposure.


## RC.15 Foundation consolidation

Canonical Foundation hub: `docs/FOUNDATION.md`. It links the architecture, governance, ecosystem, API and AI domains to the single official roadmap without creating a parallel plan.

## Project Health Dashboard

Canonical view: `docs/project/PROJECT_HEALTH_DASHBOARD.md`. Structured source: `docs/project/project_health.json`. Renderer: `tools/update_project_health.py`.

## Target Validation Pack

Canonical policy: `docs/target-validation/TARGET_VALIDATION_POLICY.md`. The pack collects, validates and immutably imports Home Assistant 2026.x runtime, compatibility, HACS, security and UX/accessibility evidence without storing credentials.

## Phase 7B status

Home Assistant certification enablement is implemented. Live-target execution remains pending and release approval is not granted.

## Pre-Phase 7C documentation consolidation

The current canonical package is `1.1.0-rc.15-phase7c-github-publication-ready`. Runtime lifecycle cleanup and SIP shutdown hardening are included; no feature was added. Repository-local certification passes with 332/332 tests and all available local gates. Ruff and mypy remain pending in CI because the local package service was unavailable. Active handoffs, generated health artifacts, repository inventory, localization support levels and documentation consistency validators are synchronized during Phase 7C — Release Candidate Approval.

## Release Candidate Dossier

The authoritative Phase 7C dossier is `docs/release/RELEASE_CANDIDATE_DOSSIER.md`; decision remains BLOCKED.
