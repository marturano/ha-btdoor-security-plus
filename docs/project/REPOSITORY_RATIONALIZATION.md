# Repository Rationalization

## Status

Phase 6B is implemented as a governed, repeatable repository analysis. It establishes a single-source-of-truth registry, dependency graph, reference integrity checks and repository metrics.

## Canonical artifacts

- `docs/project/canonical_documents.json` — machine-readable registry.
- `docs/project/CANONICAL_DOCUMENTS.md` — human-readable registry.
- `docs/project/repository_dependency_map.json` — complete dependency graph.
- `docs/project/REPOSITORY_DEPENDENCY_MAP.md` — summarized dependency map.
- `docs/project/repository_metrics.json` — metrics, candidates and defects.

## Command

```bash
python tools/repository/analyze_repository.py --check
```

## Deletion rule

No file is deleted merely because it has no textual inbound reference. Home Assistant runtime resources, tests, localized content, ADRs and historical release evidence can be convention-loaded or intentionally independent. Deletion requires one of the following:

1. exact duplication with a retained canonical source;
2. a registered supersession and migrated references;
3. confirmed absence from runtime, packaging, tests, documentation and continuity contracts.

## Single-source-of-truth rule

Every governed area has one canonical document. Derived documents may provide indexes, operational checklists or handoff summaries, but may not redefine policy or status independently.

## CI and governance

The rationalization check is part of the Governance Automation Framework and must pass during Validation Maintenance and Update, repository restructuring and release readiness.
