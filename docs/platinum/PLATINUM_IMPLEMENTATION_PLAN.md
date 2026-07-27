# Platinum Implementation Plan

> **Document status:** Historical / informational  
> **Normative:** No  
> **Active roadmap scope:** Excluded  
> **Current policy:** GOLD is the permanent governed maximum. This document is retained only as historical engineering evidence.


## Release strategy

Do not implement Platinum in the 1.1.0 final stabilization branch. Target a dedicated 1.2 programme.

## Phase P1 — External client package design

Deliverables:

- package boundary for cloud, SIP, media transport models, exceptions, and authentication;
- package name and ownership decision;
- PyPI publishing workflow with sdist and wheel;
- issue tracker and security policy;
- semantic-versioning policy;
- architecture ADR.

Exit gate: integration-specific Home Assistant imports are absent from the client package.

## Phase P2 — Async client extraction

Deliverables:

- async cloud client;
- async SIP/TLS client;
- cancellation-safe tasks;
- injected `aiohttp.ClientSession`;
- typed public models;
- transport tests and fake servers.

Exit gate: no external network communication remains in the integration repository layer.

## Phase P3 — Integration adapter migration

Deliverables:

- manifest requirement pinned to the client package;
- Home Assistant session injection at every construction path;
- runtime adapter preserving current entities, services, events, and diagnostics;
- compatibility and migration tests.

Exit gate: behaviour and coverage remain at or above the current Gold baseline.

## Phase P4 — Strict typing

Deliverables:

- `ConfigEntry[BTDoorRuntimeData]` alias;
- strict annotations across production modules;
- typed event, service, diagnostics, cloud, SIP, and support models;
- package `py.typed` marker;
- reproducible mypy strict gate.

Exit gate: strict mypy passes without blanket suppressions.

## Phase P5 — Platinum validation

Deliverables:

- generated Quality Scale evidence;
- Home Assistant target-runtime validation;
- cancellation/leak validation;
- HACS install/upgrade/uninstall cycle;
- dependency publication and installation evidence;
- updated documentation and handoff.

Exit gate: all three Platinum rules are generated `done`; no rule is promoted by assertion.

## Estimated scope

| Phase | Relative effort | Risk |
|---|---:|---:|
| P1 | Medium | Medium |
| P2 | High | High |
| P3 | High | High |
| P4 | High | Medium |
| P5 | Medium | Medium |

## Go/no-go decision

Proceed only after 1.1.0 Final is stable and the external-library maintenance commitment is accepted. The cost is justified if the project aims for Home Assistant Core inclusion, Works with Home Assistant alignment, or long-term multi-integration reuse. For a HACS-only integration, Gold may offer the better risk/benefit balance.
