# Release Candidate Dossier — BTDoor Security+ 1.1.0 Final

**Generated:** 2026-07-27  
**Exact package:** `1.1.0-rc.15-phase7c-github-publication-ready`  
**Official phase:** Phase 7C — Release Candidate Approval  
**Decision:** **BLOCKED**  
**Phase 7D authorized:** **No**

## Executive conclusion

The repository-local implementation, governance, documentation, localization and certification framework are ready for final field certification. The operator support bundle collected on 2026-07-27 is accepted as validated supporting runtime evidence (`EV-TARGET-002`), but it is not sufficient to close the formal target-runtime, performance, security, publication, UX or external Quality Scale blockers.

The release must remain blocked until the exact-package evidence below is completed. Evidence coverage is descriptive and cannot override a single blocking item.

## Release contract

- Supported Home Assistant series: **2026.x**.
- Mandatory reference validation target: **2026.7.x**.
- Release minimum and governed maximum: **Integration Quality Scale GOLD**.
- Feature freeze: active.
- Final approval authority: Release Decision Engine, based on validated evidence and accepted risk state.

## Gate and evidence matrix

| Gate | Current status | Validated evidence | Blocking evidence still required |
|---|---|---|---|
| Definition of Ready | PASS | `EV-GOV-001` | None |
| Architecture | PASS | `EV-ARCH-001` | None |
| Quality | PASS | `EV-QUAL-001`, `EV-CERT-001` | None |
| Security | BLOCKED | `EV-SEC-001`, `EV-CERT-003`, partial `EV-TARGET-002` | `EV-SEC-002` |
| Performance | BLOCKED | `EV-PERF-001`, partial `EV-TARGET-002` | `EV-PERF-002` |
| Documentation and UX | BLOCKED | `EV-DOC-001`, `EV-I18N-001`, `EV-CERT-004` | `EV-UX-001` |
| Compatibility | BLOCKED | `EV-CERT-002`, partial `EV-TARGET-002` | `EV-COMP-001` |
| Release Readiness | PASS (package-local) | `EV-REL-001`, `EV-HAND-001` | None |
| Publication | BLOCKED | Repository assets only | `EV-PUB-001` |
| Home Assistant Quality Scale | BLOCKED for final external sign-off | Internal GOLD workflow | `EV-HAQS-001` |

## Accepted runtime evidence

`EV-TARGET-002` demonstrates, for the collected runtime session:

- framework health score 100/100;
- cloud availability;
- certificate and private-key presence;
- successful SIP registration;
- established TLS 1.3 session;
- observable and closed dialog/media lifecycle;
- no recorded runtime error;
- zero dropped debug records.

It does **not** establish the Home Assistant Core version, lifecycle restart/reload recovery, measured performance thresholds, HACS install/update/rollback, interactive UX/accessibility, or complete security sign-off. The observed `verify_server: false` remains a review item and is not interpreted as either a vulnerability or an accepted exception without documented protocol context.

## Blocking evidence completion plan

### `EV-COMP-001` — Compatibility lifecycle

Required evidence:

- exact Home Assistant Core version;
- supported 2026.x lifecycle execution;
- at least one complete run on 2026.7.x;
- clean setup, config-entry reload and Home Assistant restart;
- entity/device continuity and duplicate-registry check;
- removal and reinstallation verification.

### `EV-PERF-002` — Runtime benchmark

Required measured values and environment metadata:

- integration setup duration;
- config-entry reload duration;
- restart recovery duration;
- steady-state memory observation;
- reconnect behavior and retry count;
- pass/fail evaluation against documented thresholds.

### `EV-SEC-002` — Runtime security certification

Required evidence:

- secrets and log-redaction review;
- support-bundle sanitization review;
- TLS verification-mode explanation and sign-off;
- certificate/private-key storage and lifecycle review;
- confirmation that diagnostics contain no sensitive identifiers.

### `EV-PUB-001` — HACS and GitHub lifecycle

Required evidence:

- exact-package HACS install;
- update from the supported previous package;
- rollback or recovery procedure;
- HACS Action and hassfest result;
- release assets, tag, manifest and checksums.

### `EV-UX-001` — Interactive UX/accessibility

Required evidence:

- config and options flow review;
- entity names, descriptions and error messages;
- keyboard and screen-reader relevant labeling where applicable;
- dashboard/control clarity;
- supported-language review for EN, IT, FR, NL, DE and ES.

### `EV-HAQS-001` — Final Gold evidence

Required evidence:

- current rule-by-rule Gold mapping;
- references to exact-package tests and documentation;
- external/CI checks required by the project policy;
- explicit confirmation that no lower-tier rule regressed.

## Open release risks

| Risk | Severity | Reason release remains blocked |
|---|---|---|
| `RISK-001` | CRITICAL | Measured target performance baseline unavailable |
| `RISK-002` | HIGH | Final target security review not signed off |
| `RISK-003` | HIGH | Final Home Assistant compatibility lifecycle incomplete |
| `RISK-004` | HIGH | HACS/GitHub publication lifecycle not validated |
| `RISK-005` | MEDIUM | Interactive accessibility evidence missing |

## Approval criteria

The Release Decision Engine may return `APPROVED` only when:

1. every blocking evidence item is `VALIDATED` for the exact package;
2. no CRITICAL or HIGH risk remains open without a formally approved exception;
3. Quality Scale GOLD remains proven;
4. all repository, governance, documentation, handoff and release-readiness gates pass;
5. the final release manifest, inventory and checksums are reproducible.

Until then, this dossier is the authoritative Phase 7C summary and Phase 7D must not begin.
