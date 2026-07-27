# ADR-0025 — Active roadmap and release handoff are packaged artifacts

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

During the RC.7 cleanup, historical planning files were archived but the approved post-Core roadmap and a self-contained continuation handoff were not restored as active documents. This made future work vulnerable to an incorrect roadmap reconstruction.

## Decision

Every release archive must contain an active, version-aligned project manifest, product roadmap, milestone document, decisions/constraints record, feature validation matrix, documentation index and self-contained new-chat handoff.

Historical numbering remains archived. The active roadmap is 1.1–2.0:

`Core Stable → Universal Door Security+ Bridge → Video Core → Audio & Call Control → Voicemail Center → Multimedia Timeline → BTicino/Netatmo Security Cameras → Smart Notifications → AI Services Platform`.

## Consequences

- Documentation continuity becomes a release gate.
- Cleanup work may archive obsolete documents only after active replacements exist.
- Any architecture, entity-contract or roadmap change requires a handoff update in the same build.
- Validation tests must assert that continuity documents exist and reference the current version.
