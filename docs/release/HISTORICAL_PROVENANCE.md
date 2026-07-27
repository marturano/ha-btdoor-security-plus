# Historical Provenance Register

## Purpose

BTDoor Security+ has always been the same integration. Early packages used several provisional version schemes while the architecture was still being discovered. This register preserves traceability to old archives, tests and ADR metadata without exposing those schemes as the current product history.

## Canonical product history

| Canonical milestone | Meaning | Historical development labels included |
|---|---|---|
| 1.0 Foundation | Functional and architectural base of the integration | 3.x experimental work; 4.0 alpha series; 5.0/5.1 beta series; 6.0 release candidates; 6.0.0 and 6.0.1; early 6.1 alphas/betas/RCs through the pre-renumbering checkpoint |
| 1.1 Core Stable | Stabilization, Home Assistant 2026.x hardening, native gate button, dedicated voice bridge and final release governance | late 6.1 RC work continued as 1.1.0-rc.6 and later |

## Interpretation rules

1. Historical labels remain unchanged inside archived release notes, old test filenames and ADR acceptance metadata.
2. Active documentation uses only the canonical 1.0/1.1 line.
3. A historical label does not imply an independently supported release family.
4. Features are assigned to the canonical milestone in which they became part of the retained architecture, not by mechanically translating the old number.
5. Git tags and checksums remain the authoritative forensic record for exact old packages.

## Feature provenance summary

| Capability retained today | Principal historical evidence | Canonical placement |
|---|---|---|
| Domain migration and async compliance | ADR-0007, ADR-0008 | 1.0 Foundation |
| Support artifact identity and Support Bundle v2 | ADR-0009, ADR-0010 | 1.0 Foundation |
| Certificate migration and modular diagnostics | ADR-0011, ADR-0012 | 1.0 Foundation |
| Persistent snapshots and Developer Toolkit | ADR-0013, ADR-0014 | 1.0 Foundation |
| SIP identity and media lifecycle | ADR-0015, ADR-0016 | 1.0 Foundation |
| Observability entities and runtime state provider | ADR-0017, ADR-0018 | 1.0 Foundation |
| Device model and event wiring | ADR-0019 through ADR-0022 | 1.0 Foundation |
| Documentation framework | ADR-0023 | 1.0 Foundation, revised in 1.1 |
| Home Assistant 2026.x hardening | archived 6.1 RC.4 evidence | 1.1 Core Stable |
| Native gate button and dedicated voice bridge | 1.1 RC.6–RC.7 | 1.1 Core Stable |
| Roadmap and handoff governance | ADR-0025 | 1.1 Core Stable |

## Known anomaly

`ADR-0024` is not present in the supplied source archive. No replacement decision is invented. The number is reserved until Git history or an earlier package proves whether an ADR existed.
