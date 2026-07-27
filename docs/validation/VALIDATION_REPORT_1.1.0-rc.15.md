# Consolidated Validation Report — 1.1.0-rc.15

**Status:** Current consolidated validation evidence  
**Release:** `1.1.0-rc.15`  
**Maintenance owner:** Validation Maintenance and Update gate  
**Rule:** This document replaces fragmented RC.15 validation and integrity reports. Generated results must be refreshed whenever code, documentation, workflows, release metadata, translations, compatibility claims, security rules or repository structure change.

## Executive result

The retained validation evidence covers repository integrity, documentation, roadmap, ADRs, architecture, ecosystem, AI provider contracts, API, translations, compatibility, handoff, release completeness, links, Mermaid content and QA. Runtime, real-device, GitHub publication and HACS lifecycle evidence remain release-specific and must not be inferred from static checks.

## Evidence provenance

The sections below preserve the material previously distributed across individual validation files. Future runs should update this consolidated report and `VALIDATION_REGISTER.md`, rather than creating parallel reports without a lifecycle entry.

---

## Source consolidated: `ADR_INTEGRITY.md`

# ADR Integrity Check

Status: **Release-blocking**

## Purpose

Verifies sequential ADR identifiers, required status sections, index registration, and traceability for governance or contract changes.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `AI_DOCUMENTATION_INTEGRITY.md`

# AI Documentation Integrity

Release-blocking gate validating the canonical AI document set, index coverage, status declarations, privacy baseline and non-claim of unfinished runtime adapters.

Run: `python tools/check_repository_integrity.py --check ai_documentation`.

---

## Source consolidated: `API_INTEGRITY.md`

# API Integrity Check

Status: **Release-blocking**

## Purpose

Verifies that public entities, services, events, REST, and WebSocket documentation remain present and that contract changes are paired with ADR and migration evidence.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `ARCHITECTURE_INTEGRITY.md`

# Architecture Integrity Check

**Status:** Blocking Quality Gate

The check validates that the canonical architecture index exists, required architecture documents are present, implementation references point to real repository paths and planned capabilities are explicitly labelled.

Run:

```bash
python tools/check_repository_integrity.py --check architecture
```

A release fails when a required document is absent, the architecture index omits it, or a backticked implementation path beginning with `custom_components/` does not exist.

---

## Source consolidated: `COMPATIBILITY_INTEGRITY.md`

# Compatibility Matrix Check

Status: **Release-blocking**

## Purpose

Verifies that Home Assistant and device/voice-assistant compatibility documents exist and distinguish static, simulated, user-evidence, and real-device validation.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `CONTINUATION_PACKAGE_VALIDATION_2026-07-22.md`

# Continuation Package Validation — 2026-07-22

## Scope

Governance, documentation policies, quality/security/benchmark registers and complete handoff continuity package.

## Results

- Full test suite: passed, 182 tests.
- Repository integrity checker: passed.
- Required governance artifacts: present.
- Handoff recovery prompt: current baseline `1.1.0-rc.15` and self-contained.
- Official roadmap: not modified by this package.

## Limitations

This validation does not claim runtime benchmark execution, real Home Assistant installation, online GitHub publication or HACS Final Release validation. Those remain mandatory before `1.1.0 Final`.

---

## Source consolidated: `DOCUMENTATION_INTEGRITY.md`

# Documentation Integrity Check

Status: **Release-blocking**

## Purpose

Verifies canonical documents, document lifecycle metadata, required documentation domains, and absence of conflicting active sources of truth.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `ECOSYSTEM_INTEGRITY.md`

# Ecosystem Integrity Check

This blocking gate validates the ecosystem documentation contract.

It requires:

- the canonical ecosystem index;
- support, capability, adapter and discovery documents;
- every product-family document listed in the index;
- mandatory `Status`, `Capability scope`, `Home Assistant mapping principles`, `Dependencies and acceptance`, and `Related documentation` sections;
- a support-matrix row for every product family;
- explicit language preventing roadmap material from being represented as current runtime support.

Run with:

```bash
python tools/check_repository_integrity.py --check ecosystem
```

---

## Source consolidated: `HANDOFF_INTEGRITY.md`

# Handoff Integrity Check

Status: **Release-blocking**

## Purpose

Verifies the complete continuity package, current release references, Recovery Prompt, continuity status, and integrity results.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `LINK_VALIDATION.md`

# Link Integrity Check

Status: **Release-blocking**

## Purpose

Verifies relative Markdown links in active documentation and reports unresolved local targets.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `MERMAID_VALIDATION.md`

# Mermaid Validation

**Status:** Blocking structural Quality Gate

The repository validator performs deterministic structural checks without requiring Node.js:

- every opening ` ```mermaid ` fence is closed;
- each block begins with a supported Mermaid diagram declaration;
- empty blocks are rejected;
- obvious placeholder markers are rejected.

Run:

```bash
python tools/check_repository_integrity.py --check mermaid
```

Full rendering with Mermaid CLI is planned for CI/CD automation. Structural validation remains useful in offline release environments.

---

## Source consolidated: `PROVIDER_CAPABILITY_INTEGRITY.md`

# Provider Capability Integrity

Release-blocking gate validating the canonical capability vocabulary, provider-family matrix, local/cloud classification and explicit runtime-status column.

Run: `python tools/check_repository_integrity.py --check provider_capability`.

---

## Source consolidated: `QA_REPORT_1.1.0-rc.15.md`

# QA Report — BTDoor Security+ 1.1.0-rc.15

Date: 2026-07-22

## Decision

**Conditional PASS for isolated QA.** The repository is internally consistent and the complete local test suite passes. Release promotion still requires the CI and real-runtime gates listed below.

## Scope executed

- config-entry lifecycle and platform forwarding source review;
- runtime listener and unload symmetry review;
- entity naming, categories, device classes and event subscriptions review;
- native diagnostics and Support Bundle privacy review;
- services and response contracts review;
- HACS and manifest metadata validation;
- translation and documentation integrity gates;
- complete pytest suite;
- Python compilation and JSON parsing;
- repository and architecture integrity suites;
- release residue scan.

## Finding QA-SEC-001 — Native diagnostics privacy

Severity: **Major**
Status: **Fixed**

The native Home Assistant diagnostics endpoint previously applied a narrow redaction list to config-entry data only. Runtime fields could still contain SIP URIs, private IP addresses, call identifiers, SDP data and local filesystem paths.

### Correction

`diagnostics.py` now passes the complete diagnostics payload through the project's central `sanitize_support_data()` policy. This aligns native diagnostics with Support Bundle exports and provides:

- credential and cryptographic-material redaction;
- stable hashing of persistent identifiers;
- gateway identifier masking;
- private IPv4 masking;
- SIP call-id, branch, tag and instance hashing;
- redaction of certificate and private-key paths.

Two regression tests enforce use of the central policy and verify representative sensitive values cannot survive export.

## Lifecycle and runtime review

- Config entries use `runtime_data` and forward supported platforms asynchronously.
- Update listeners are registered with `entry.async_on_unload()`.
- Entity listeners are registered in `async_added_to_hass()` and removed through `async_on_remove()`.
- Platform unload precedes client shutdown and state persistence.
- Certificate-renewal and client-event callbacks are released during unload.
- Services are registered globally without closing over a specific config entry.
- Multi-entry service routing requires an explicit target for gate opening.

No additional release-blocking defect was found in the isolated source review.

## Entity and frontend review

- Base entities use `_attr_has_entity_name = True`.
- Diagnostic entities use `EntityCategory.DIAGNOSTIC` where appropriate.
- Timestamp sensors use `SensorDeviceClass.TIMESTAMP`.
- The gate action is exposed as a momentary button; the optional voice bridge remains a stateless switch for Alexa/Google routines.
- Brand assets are present under the integration `brand/` directory.
- Config Flow, Reconfigure, Reauth and Options Flow resources are present and translation integrity passes.

## Executed validation results

- Complete pytest suite: **PASS — 182 tests**.
- Repository Integrity Suite: **PASS — 16/16 gates**.
- Architecture dependency validation: **PASS**.
- Python compilation: **PASS**.
- Integration and HACS JSON parsing: **PASS**.
- Translation/documentation integrity: **PASS**.
- Final cache, bytecode and transient-artifact cleanup: **PASS**.

## Environment-bound gates still required

The following are not claimed as executed in this isolated environment:

- hassfest;
- HACS Action;
- Ruff CI job;
- Home Assistant compatibility matrix 2026.1–2026.7;
- clean installation, restart, reload and unload in a real Home Assistant instance;
- cloud authentication and certificate provisioning against MyHomeWeb;
- SIP registration and physical gate operation;
- Alexa, Alexa+ and Google Assistant real-account/device validation;
- real-device duplicate device/entity registry checks;
- Zigbee2MQTT interoperability where user automations bridge external entities.

## Release recommendation

Proceed to **Phase 6 — Final Validation** after the CI matrix is green and the real Home Assistant/device checklist is completed. A new release candidate is required only if those external gates expose a functional defect.

---

## Source consolidated: `RELEASE_COMPLETENESS.md`

# Release Completeness Check

Status: **Release-blocking**

## Purpose

Verifies version synchronization, release notes, validation, changelog, documentation changelog, handoff, package exclusions, and mandatory quality-gate evidence.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `REPOSITORY_STRUCTURE.md`

# Repository Structure Check

Status: **Release-blocking**

## Purpose

Verifies mandatory top-level files and canonical directories, and rejects transient caches, bytecode, secrets, and support bundles from release packages.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `ROADMAP_INTEGRITY.md`

# Roadmap Integrity Check

Status: **Release-blocking**  
Introduced: **1.1.0-rc.15**

## Guarantees

The check verifies that:

- every roadmap series listed in `ROADMAP.md` has a detail file;
- milestone identifiers are unique across all active roadmap files;
- identifiers are ordered within each series;
- every milestone has a non-empty title;
- removed or renumbered milestones are recorded in the documentation changelog and, when material, an ADR;
- roadmap files do not describe planned work as implemented;
- continuity and release documents identify roadmap changes.

## RC.15 correction

The RC.14 roadmap contained duplicate identifier `4.3`. RC.15 preserves `4.3 — Adaptive Home Experience` and renumbers `Documentation Platform` to `4.4`. The correction is recorded in ADR-0043 and the documentation changelog.

## Automated command

```bash
python tools/check_repository_integrity.py --check roadmap
```

---

## Source consolidated: `TRANSLATION_INTEGRITY.md`

# Translation Integrity Check

Status: **Release-blocking**

## Purpose

Verifies equal UI translation key coverage and required localized documentation/release-note presence for en, it, fr, de, es, and nl.

## Failure policy

A failure blocks release publication until corrected or explicitly classified as a documented environment limitation that does not invalidate the repository contract.

## Evidence

Results are recorded in `handoff/18_INTEGRITY_SUITE_RESULTS.md` and the release validation report.

---

## Source consolidated: `VALIDATION_REPORT_1.1.0-rc.15.md`

# Validation RC15

- Added governance docs
- Added Roadmap Integrity Check
- Added architecture/API/compatibility skeletons


## Phase 2 validation scope

- Architecture Integrity Check: required
- Mermaid structural validation: required
- Canonical architecture index coverage: required
- RC.15 architecture tests: required
- Production runtime changes: none intended

Environment limitation remains: full Home Assistant, hassfest, HACS and real-device validation require their dedicated environments.

## Phase 2 executed results

- Repository Integrity Suite: **12/12 PASS**
- RC.15 focused tests: **5 passed**
- Python compileall: **PASS**
- Translation QA: **PASS — 6 locales, 144 keys, 7 documents per locale**
- Localized documentation coverage: **PASS — 100% for en/it/fr/de/es/nl**
- Architecture dependency rules: **PASS**
- Markdown local-link validation: **PASS**
- Mermaid structural validation: **PASS**

The checks above were executed on the packaged Phase 2 working tree. Home Assistant runtime, hassfest, HACS validation and real-device tests were not executed in this environment.

## Phase 3 — Ecosystem Foundation

### Scope

- canonical ecosystem index and product-family contracts;
- normative support matrix;
- capability, adapter, discovery and identity models;
- ADR-0048 and ADR-0049;
- blocking Ecosystem Integrity gate;
- synchronized release notes in six supported documentation languages.

### Results

- Repository Integrity Suite: **13/13 PASS**;
- targeted RC.13–RC.15 tests: **13 passed**;
- Python compilation: **PASS**;
- Translation QA: **6 locales, 144 keys, 7 documents per locale**;
- localized documentation coverage: **100%**;
- architecture dependency rules: **PASS**;
- active Markdown links: **PASS**;
- Mermaid structural validation: **PASS**;
- ecosystem truthfulness and coverage: **PASS**.

### Runtime limitation

No broad BTicino/Netatmo runtime adapter was added. The active integration remains BTDoor Security+ focused. Home Assistant runtime, hassfest, HACS and real-device validation were not executed in this environment.

## Phase 4 — AI Platform Foundation

Validation scope includes the canonical AI document set, capability vocabulary, provider matrix, privacy/safety requirements, ADR traceability, Mermaid structure, links, Python compilation and focused regression tests. No Home Assistant runtime, external AI provider, HACS, hassfest or real-device validation was executed in this environment.

## Full-suite limitation observed in Phase 4

The focused RC.15 Phase 1–4 suite passes (13 tests). The legacy full repository suite is not a release-pass signal in this isolated environment: three modules fail collection because Home Assistant/runtime package surfaces are unavailable, and the remaining broad run reports 17 historical failures, mostly stale release-version assertions plus pre-existing runtime/import expectations. Phase 4 changes are documentation, governance, tests and integrity tooling only; these failures were not introduced or hidden. They must be triaged during stabilization with a real Home Assistant test environment.
## RC.15 Phase 5 — API Foundation validation

- Repository Integrity Suite: **16/16 PASS**.
- Focused RC.15 Phase 1–5 tests: **17 passed**.
- Python compileall for integration, tools and tests: **PASS**.
- Every top-level action in `services.yaml` is documented in `docs/api/SERVICES.md`.
- Alexa, Alexa+ and Google Assistant exposure boundaries: **PASS**.
- REST and WebSocket implementation claims: **none; contract-only status retained**.
- Home Assistant 2026.7 runtime, real Alexa/Alexa+ accounts and real Google Assistant devices were not available in this isolated environment; real-device validation remains required.

## Repository Integrity audit — Step 3

### Scope

- canonical repository structure and release-root contents;
- cache, temporary file, nested archive and sensitive-filename scan;
- manifest, HACS metadata and JSON validity;
- repository, architecture, documentation and translation gates;
- CI regression command defined by `.github/workflows/validate.yml`;
- legacy test isolation where tests create temporary package stubs.

### Corrections applied

- Removed stale `1.1.0-rc.11` assertions from the RC6a and RC7 regression tests. The tests now verify that the manifest contains an RC version and that `const.py` exposes the identical version, avoiding false failures on later release candidates.
- Isolated the Call Journal beta.2.1 unit-test package stubs under a test-only namespace so they no longer overwrite the real `custom_components.btdoor_security_plus` and `event_bus` modules during broad pytest collection.

### Executed results

- Repository Integrity Suite: **16/16 PASS**.
- Architecture dependency rules: **PASS**.
- Localized documentation coverage: **PASS — 100% for en/it/fr/de/es/nl**.
- Translation QA: **PASS — 6 locales, 144 keys, 7 documents per locale**.
- Python compilation for integration, tools and tests: **PASS**.
- Integration and HACS JSON parsing: **PASS**.
- CI release-regression command: **PASS — 21 tests**.
- Repository residue scan: **PASS** — no caches, bytecode, temporary files, logs, nested ZIP files or common sensitive artifacts retained in the release tree.

### Environment-bound validation

`tools/check_ha_compatibility.py` requires an installed Home Assistant version and is intentionally executed by the CI compatibility matrix. The local isolated environment does not contain Home Assistant. Hassfest, HACS validation, the Home Assistant compatibility matrix and real-device tests therefore remain CI/runtime gates rather than locally claimed results.

## Legacy Test Cleanup — Step 4

### Scope

- removal of stale release-version assertions tied to alpha, 6.0.x and earlier RC builds;
- replacement of brittle source-text checks with assertions matching the current implementation;
- isolation of pure unit tests from Home Assistant runtime imports;
- elimination of eager manager-package imports that caused cross-test module pollution;
- restoration of media lifecycle tests through the supported SIP client constructor;
- execution of the complete repository pytest suite.

### Corrections applied

- `RuntimeEventBus` now imports Home Assistant's `Store` only for type checking, keeping the event model and bus unit-testable without a Home Assistant installation.
- Timeline aggregation was moved to the pure `build_timeline_summary()` support-model helper; `DeveloperTools` delegates to it and the unit test no longer imports the Home Assistant-bound developer module.
- `managers/__init__.py` now exposes manager APIs lazily, preventing unrelated manager dependencies and test stubs from being imported as package side effects.
- Historical regression tests now validate the current `1.1.0-rc.15` release contract instead of obsolete alpha, 6.0.x, RC6b or RC14 literals.
- Source-level checks were updated for the current secure support-export directory creation and compact Event Bus history API.
- Device-name catalog expectations were aligned with the six-device catalog currently implemented.
- Media lifecycle persistence tests now instantiate `BticinoSipClient` through its supported constructor rather than bypassing initialization with `object.__new__`.

### Executed results

- Complete pytest suite: **PASS — 180 tests**.
- Repository Integrity Suite: **16/16 PASS**.
- Architecture dependency rules: **PASS**.
- Python compilation for integration and tests: **PASS**.
- Repository residue cleanup after validation: **PASS**.

### Environment-bound validation

Ruff is part of the GitHub Actions validation job but was not installed in this isolated execution environment, so no local Ruff result is claimed. Hassfest, HACS, the Home Assistant 2026.1–2026.7 compatibility matrix and real-device tests remain CI/runtime gates.

## Quality Assurance — Step 5

### Scope

- lifecycle, runtime callback and unload symmetry review;
- entity metadata and listener lifecycle review;
- services, Assist and voice-bridge contracts;
- native diagnostics and Support Bundle privacy;
- manifest, HACS, JSON, translations, documentation and repository gates;
- complete local regression suite.

### Correction applied

Native Home Assistant diagnostics now use the central `sanitize_support_data()` export policy. This closes a privacy gap where runtime SIP URIs, private IP addresses, call identifiers, SDP content and local certificate paths could survive the narrower config-only redaction previously used. Regression tests verify the central policy is used and representative sensitive data is removed.

### Executed results

- Complete pytest suite: **PASS — 182 tests**.
- Repository Integrity Suite: **16/16 PASS**.
- Architecture dependency rules: **PASS**.
- Python compilation: **PASS**.
- Integration and HACS JSON parsing: **PASS**.
- Final release-tree residue cleanup: **PASS**.

### Environment-bound validation

Hassfest, HACS Action, Ruff, the Home Assistant 2026.1–2026.7 compatibility matrix, real MyHomeWeb/SIP devices and real Alexa/Alexa+/Google Assistant accounts remain CI/runtime gates and are not claimed as locally executed. See `docs/quality/QA_REPORT_1.1.0-rc.15.md`.

## Final Governance Closure — Step 6.4A

### Scope

- replacement of the root governance placeholder with the canonical project governance model;
- definition of roles, decision authority, acceptance criteria, release promotion, compatibility and deprecation policy;
- explicit source-of-truth precedence and canonical-document map;
- verification that governance links to, rather than duplicates, the Foundation, roadmap, ADRs and specialist policies.

### Correction applied

`PROJECT_GOVERNANCE.md` is now a normative governance entry point instead of a placeholder. It preserves the official roadmap as the only planning authority and the Foundation as the architectural authority. Repository, contribution and security rules remain delegated to their existing canonical documents.

### Executed results

- Governance link-target verification: **PASS**.
- Repository Integrity Suite: **16/16 PASS**.
- Architecture dependency rules: **PASS**.
- Complete pytest suite: **PASS — 182 tests**.
- Python compilation: **PASS**.
- Release-tree cleanup after validation: **PASS**.

## Gate workflow and Project Health Dashboard update — 2026-07-22

- Gate-based workflow adopted through ADR-0057.
- Project Health Dashboard source, renderer and canonical Markdown view added.
- Initial weighted Final-readiness score: **74/100 — WATCH**.
- Blocking domain: measured Performance and Benchmark baseline.
- Additional Final evidence not started: Security, UX/Accessibility, runtime Compatibility and HACS/GitHub Publication.
- Pytest suite: **185 tests PASS** after dashboard integration.
- Orphan/Hygiene Check: PASS after removing generated caches.
- Repository Integrity Suite: **16/16 PASS**.
