# BTDoor Security+ Foundation

The Foundation is the canonical technical and governance baseline for BTDoor Security+. It defines **how the project is built, maintained, validated and extended**. It complements the official roadmap but never replaces it.

## Foundation and Roadmap

The two sources have different responsibilities:

- the [official roadmap](roadmap/ROADMAP.md) defines **what the project will become** and when capabilities may be promoted into committed milestones;
- the Foundation defines **how the project is currently structured**, which contracts are normative, and which engineering rules must remain true while the roadmap evolves;
- uncommitted ideas belong only in [FUTURE_BACKLOG.md](roadmap/FUTURE_BACKLOG.md);
- planned behavior must never be described as implemented behavior.

The roadmap under `docs/roadmap/` is the only official roadmap. Foundation documents may reference it, but must not create parallel milestones, alternative numbering or competing delivery plans.

## Canonical Foundation domains

| Domain | Canonical entry point | Purpose |
|---|---|---|
| Architecture | [Architecture documentation](architecture/README.md) | Runtime structure, ownership, module boundaries, entity and event models, pipelines, diagnostics and isolation. |
| Governance | [Project governance](../docs/project/PROJECT_CONSTITUTION.md), [repository policy](../docs/repository/REPOSITORY_POLICY.md), [document lifecycle](governance/DOCUMENT_LIFECYCLE.md) | Decision authority, repository rules, documentation lifecycle, contribution and release discipline. |
| Ecosystem | [Ecosystem documentation](ecosystem/README.md) | Capability model, adapter boundaries, discovery, identity and the implemented-versus-planned support model. |
| API | [API Foundation](api/README.md) | Public Home Assistant entities, actions, events, errors, versioning, security and assistant exposure. |
| AI | [AI Platform Foundation](ai/README.md) | Provider-neutral AI contracts, privacy, orchestration, normalization and automation boundaries. |

Supporting engineering sources include:

- [Architecture principles](../ARCHITECTURE_PRINCIPLES.md)
- [Project manifest](../PROJECT_MANIFEST.md)
- [ADR index](adr/README.md)
- [Compatibility matrix](compatibility/COMPATIBILITY_MATRIX.md)
- [Security baseline](security/SECURITY_BASELINE.md)
- [Performance baseline](benchmarks/BASELINES.md)
- [Release checklist](release/RELEASE_CHECKLIST.md)

## Source-of-truth hierarchy

When documents appear to conflict, use this order:

1. executable runtime behavior and validated tests;
2. current public contracts in the API and compatibility documentation;
3. accepted ADRs and architecture rules;
4. active Foundation documentation;
5. the official roadmap for planned evolution;
6. archived material as historical evidence only.

A document must not claim runtime support without corresponding implementation or validation evidence.

## Architectural decisions

Significant architectural decisions require an Architecture Decision Record in [`docs/adr/`](adr/README.md). Before adding an ADR, verify that an equivalent decision does not already exist. ADRs explain decisions; they do not replace implementation documentation, API contracts or roadmap milestones.

## Evolution rules

Foundation changes must follow these rules:

1. Extend or improve an existing canonical document before creating a new one.
2. Do not duplicate architecture, governance, ecosystem, API or AI guidance.
3. Preserve useful knowledge when replacing documentation; migrate content, update references and archive normative predecessors when required.
4. Keep implemented, contract-only and planned capabilities explicitly separated.
5. Update documentation, examples, tests, translations and release records when a public capability changes.
6. Preserve compatibility with Home Assistant 2026.x, the supported Home Assistant Python baseline, HACS and hassfest.
7. Validate changes with the Repository Integrity Suite and relevant focused checks whenever possible.
8. Record material architectural decisions through a non-duplicative ADR.

## Release 1.1.0 boundary

For the road to `1.1.0 Final`, Foundation work is limited to consolidation, correctness, traceability and production readiness. New capabilities that are not required by an approved roadmap milestone or by release correctness must be deferred to [FUTURE_BACKLOG.md](roadmap/FUTURE_BACKLOG.md) or a later release.

Completion of the Foundation does not mean every future platform capability is implemented. It means the current repository has a coherent, navigable and validated technical baseline for the release.
