# Phase 7C — Release Candidate Dossier

**Current package:** `1.1.0-rc.15-phase7c-github-publication-ready`  
**Status:** Phase 7C active — BLOCKED  
**Phase 7D:** Not authorized

## Completed

- Consolidated the exact-package gate, evidence and risk state into `docs/release/RELEASE_CANDIDATE_DOSSIER.md`.
- Added machine-readable `docs/release/RELEASE_CANDIDATE_DOSSIER.json`.
- Linked the accepted 2026-07-27 runtime support evidence without promoting it to blocking certification evidence.
- Preserved Home Assistant 2026.x support with 2026.7.x as the mandatory reference validation target.
- Preserved Quality Scale GOLD as the release minimum and governed maximum.

## Immediate resume point

Execute the remaining exact-package field validations for `EV-COMP-001`, `EV-PERF-002`, `EV-SEC-002`, `EV-PUB-001`, `EV-UX-001` and `EV-HAQS-001`. Update the dossier and evidence register only from reviewed artifacts. Do not start Phase 7D until the Release Decision Engine returns `APPROVED`.

## Workflow and permanent project rules

The canonical repository, official workflow, `docs/roadmap`, governance gates, translation framework, compatibility matrix, documentation impact analysis, evidence register, risk register, Release Decision Engine and complete self-contained handoff remain mandatory. No feature work is allowed during the 1.1.0 feature freeze.
