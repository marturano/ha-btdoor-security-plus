# Repository Policy

## Purpose

This is the canonical policy for repository structure, source-of-truth handling, packaging, online publication and maintenance. GitHub-specific publication requirements are further detailed in `GITHUB_REPOSITORY_POLICY.md`.

## Core rules

1. Search before creating a document; update the canonical document when one exists.
2. A replacement document requires an archive copy, a compatibility pointer where external links may exist, and a documentation changelog entry.
3. Active documents must not contradict the Project Constitution, Project Execution Contract, Project Memory, official roadmap or accepted ADRs.
4. Generated reports carry a release identifier and are evidence, never architecture or governance authority.
5. Cache, build residue, editor files, temporary output and nested release archives are not release artifacts.
6. Secrets, tokens, certificates, personal data and unsanitized diagnostics must never be committed or packaged.
7. Release packages must be reproducible, include the complete Continuation Package and exclude transient artifacts.
8. Git branches, tags, manifests, release assets, checksums and documentation must remain mutually consistent.
9. Every Final Release requires documented GitHub and HACS validation before publication.

## Canonical directories

- `custom_components/`: runtime integration.
- `docs/`: active, generated and archived documentation.
- `docs/roadmap/`: sole authoritative product roadmap.
- `docs/repository/`: repository, GitHub, HACS and publication policy.
- `handoff/`: mandatory Project Continuity Package.
- `tests/`: regression and release-contract tests.
- `tools/`: validation and maintenance tools.
- `blueprints/`, `dashboards/`: supported user assets.

## Document lifecycle

Normative content is consolidated into one canonical document per topic. Superseded source material is consolidated into the canonical document and removed from active packages. Compatibility pointer files are not retained solely for historical tests; current tests must target canonical entry points.
