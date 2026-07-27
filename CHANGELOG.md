## Phase 7C — Governance and CI audit remediation

- Prevented Python bytecode caches from being written inside the checked-out repository during GitHub validation, governance and compatibility jobs.
- Removed packaged runtime logs and local cache directories that violated repository integrity and hygiene gates.
- Regenerated repository rationalization metadata after cleanup.
- Verified repository integrity and hygiene gates locally; the full pytest suite reached a clean pass under the isolated GitHub-style plugin configuration during the audit.
- Kept Ruff formatting and mypy as mandatory remote GitHub checks.


## Phase 7C — GitHub sandbox execution fix

- Made the isolated validation workflow invoke `github_sandbox_validate.sh` explicitly through Bash.
- Removed the GitHub Actions dependency on the executable bit, preventing exit code 126 on repositories prepared from Windows or ZIP archives.
- Verified the workflow YAML and shell syntax locally.


## Phase 7C — GitHub publication readiness

- Added a deterministic repository publication preflight.
- Expanded CI from a small regression subset to the complete pytest suite.
- Made Ruff and mypy explicit blocking CI checks.
- Documented exact-commit GitHub, release and HACS traceability requirements.
- Kept remote HACS/hassfest/GitHub results pending until executed on GitHub.


## 1.1.0-rc.15 — Phase 7C Release Candidate Dossier

- Added the authoritative human-readable and machine-readable Release Candidate Dossier.
- Consolidated gate, evidence, risk, compatibility and Quality Scale status for the exact package.
- Preserved `BLOCKED` until all external and target evidence is validated.


## 1.1.0-rc.15 — Phase 7C runtime evidence intake

- accepted the 2026-07-27 operator support bundle as partial supporting evidence;
- retained only selected redacted JSON evidence and generated SHA256 inventory;
- registered `EV-TARGET-002` as validated, non-blocking evidence;
- documented healthy cloud, certificate, SIP, TLS and media runtime findings;
- kept all external blocking evidence pending because lifecycle, metrics, HACS, UX and exact Home Assistant version are not demonstrated;
- recorded `verify_server: false` for explicit security disposition without changing runtime behavior.
## Phase 7C local certification — 2026-07-23

- Certified the exact package with 332/332 tests passing.
- Passed repository integrity, hygiene, governance, handoff, localization, architecture, Quality Scale, certification and production-audit gates.
- Recorded Ruff and mypy as not executed locally because the configured package service was unavailable; CI execution remains mandatory.
- Preserved the `BLOCKED` Release Decision pending target and external evidence.

#
## Phase 7C Runtime Lifecycle Hardening

- cleaned up support-debug and SIP resources when config-entry setup fails before Home Assistant can unload the entry;
- centralized runtime cleanup for setup rollback and normal unload;
- awaited SIP call-timeout task cancellation during shutdown;
- added lifecycle regression tests and verified 332 passing tests with an isolated pytest runner;
- added no feature and kept the release decision blocked pending target evidence.

#
## Pre-Phase 7C Documentation & Governance Final Consolidation

- synchronized the canonical package identity across active handoffs, Project Health sources and generated documentation;
- regenerated the full repository inventory and separated current operational handoffs from historical snapshots;
- marked Bronze, Silver and Platinum-readiness records as non-normative historical evidence;
- clarified GOLD as the permanent governed maximum and clarified Release Readiness versus final Release Decision semantics;
- completed localized RC15 release-note paragraphs for all six full-documentation locales;
- formalized runtime-locale versus full-documentation-locale support levels;
- added blocking documentation consistency checks for package identity, inventory completeness, historical metadata and localized release-note contamination;
- changed no runtime integration behavior.

#
### QS-21 — Gold Exception Translation Completion

- replaced user-facing positional service/entity errors with translated Home Assistant exceptions;
- added six stable exception keys with placeholder support across all 17 supported locales;
- added behavioural translation-key and locale-parity tests;
- regenerated measured coverage at 95.08% with 328 coverage-gate tests passing;
- promoted the repository Quality Scale self-assessment from Silver to Gold.

## QS-20 Silver Achievement

- Added behavioural coverage for complete setup-entry orchestration, event bridging, scheduled renewal and Support Bundle generation.
- Added residual SIP SDP, media application and Digest authentication coverage.
- Increased measured integration coverage from 92.55% to 95.08% with 325 passing tests.
- Completed all 10 Silver rules and advanced the repository Quality Scale self-assessment from Bronze to Silver.
- Added ADR-0088, QS-20 Silver report and handoff 61.

### QS-19 Lifecycle and SIP Residual Coverage

- Added behavioural coverage for integration setup, schema migration, certificate storage edge cases and optional-resource unload.
- Added SIP stream framing, provisional response filtering and incomplete-body error coverage.
- Increased measured integration coverage from 91.49% to 92.55%.
- Increased `sip_client.py` coverage to 87.09%.
- Added ADR-0087, QS-19 coverage report and handoff 60.


### QS-18 Media Residual Coverage

- Added behavioural coverage for SRTP metadata edge cases, media socket lifecycle, allocation failures and partial-preparation cleanup.
- Increased measured integration coverage from 91.06% to 91.49%.
- Increased `media.py` coverage to 99.16%.
- Added ADR-0086, QS-18 coverage report and handoff 59.

## QS-17 — Developer and Lifecycle Residual Coverage

- Added behavioural coverage for Developer Tools cloud, SIP, TLS, certificate inspection and the complete diagnostic runner.
- Added strict module-state restoration for isolated Home Assistant test doubles.
- Raised measured integration coverage from 90.50% to 91.06%.
- Raised `developer.py` coverage to 84.67%.
- Added ADR-0085, QS-17 report and handoff 58.

## QS-16 — Config Flow Residual Coverage

- Added behavioural coverage for cloud discovery, provisioning data construction, SIP validation, reauthentication error mapping and options normalization.
- Raised measured integration coverage from 90.13% to 90.50%.
- Raised `config_flow.py` coverage to 95.40%.
- Added ADR-0084, QS-16 report and handoff 57.


### Quality Scale QS-14

## QS-15 — Cloud Certificate Residual Coverage

- Added behavioural coverage for cloud CSR generation, certificate decoding, PEM/DER/ZIP parsing, key matching, chain handling and provisioning failures.
- Raised measured integration coverage from 88.42% to 90.13%.
- Raised `cloud.py` coverage to 95.57%.
- Added ADR-0083, QS-15 report and handoff 56.


- Added behavioural coverage for core runtime lifecycle, rollback, Event Bus persistence, eviction, subscriptions and dispatcher behavior.
- Raised measured integration coverage from 87.63% to 88.42%.
- Raised `core/runtime.py` coverage to approximately 96%.
- Kept Silver blocked until measured coverage strictly exceeds 95%.


### Quality Scale QS-13

- Added behavioural coverage for SIP INVITE, CANCEL, BYE, timeout, REGISTER Digest authentication, proxy-auth priming and keepalive.
- Raised measured integration coverage from 83.22% to 87.63%.
- Raised `sip_client.py` coverage to approximately 82%.
- Kept Silver blocked until measured coverage strictly exceeds 95%.

## Quality Scale QS-8

- Added core lifecycle and certificate renewal behavioural tests.
- Increased cumulative integration coverage from 71.57% to 73.49%.
- Increased `__init__.py` coverage to 67.84%.
- Documented isolated-process validation for nested certification tests.


### Quality Scale QS-11

- Added behavioural coverage for adapter foundations, runtime-state API/provider and diagnostic result/bundle contracts.
- Raised measured integration coverage from 79.23% to 80.49%.
- Kept Silver blocked until measured coverage strictly exceeds 95%.

## Quality Scale QS-2 — Platform coverage

### Quality Scale QS-5
- Added behavioural coverage for core certificate helpers, media negotiation and SIP parsing/authentication.
- Raised measured integration coverage from 59.24% to 64.62% with 258 passing tests.
- Kept the Quality Scale tier at Bronze because the Silver coverage threshold remains unmet.

- Added behavioural contract coverage for binary sensors, buttons, events, switches, diagnostics, entity base classes, and device-info construction.
- Increased measured integration coverage from 35.54% to 40.59%.
- Added ADR-0070, QS-2 coverage report, and handoff 43.
- Kept Silver blocked because measured coverage remains below the greater-than-95% requirement.


## Legacy internal Quality Scale work package 7C — Silver progress

- Added deduplicated unavailable/recovered transition logging for SIP connectivity.
- Declared explicit push-platform parallel update limits.
- Added measured pytest-cov evidence and a strict Silver coverage gate.
- Kept the achieved tier at Bronze because measured integration coverage remains below 95%.

## Workflow integration - Home Assistant Quality Scale

- Made Quality Scale assessment mandatory at phase start and phase end.
- Added configurable release-minimum and desired tiers.
- Added remediation planning and conservative safe-remediation execution.
- Added a formal Quality Scale Gate to workflow governance and handoff.
# Changelog

- Added a gate-based official workflow with Project Scope, Architecture, static analysis, layered tests, accessibility, compatibility verification, repository documentation, publication readiness and continuous-improvement steps.
- Added the governed Project Health Dashboard, structured health source, renderer and handoff integration.
### Phase 6B — Repository Rationalization

### Phase 7A — Repository Production Audit

- Added a reproducible production audit covering repository essentials, HACS/Home Assistant metadata, pinned dependencies, accidental secrets, temporary artifacts, and production duplicate files.
- Integrated the audit into governance automation without allowing it to override target certification or release approval.
- Added ADR-0063, canonical audit policy, generated reports, regression tests, and handoff status.

- Added a machine-readable canonical-document registry and generated human-readable registry.
- Added repository dependency graph, reference integrity, duplicate detection and repository metrics.
- Integrated repository rationalization into governance automation and Project Health evidence.
- Added ADR-0058 and a dedicated handoff status.

## Phase 6E — Target Validation Pack

- Added schema-governed collection, validation and immutable import of Home Assistant 2026.x target evidence.
- Integrated accepted target runs with runtime, compatibility, HACS, security and UX/accessibility certification statuses.
- Added tests preventing incomplete target runs from self-certifying a release.

## [Unreleased]

### Quality Scale QS-6
- Added behavioural coverage for developer/support tooling, including health checks, retention, support bundles and debug cleanup.
- Raised measured integration coverage from 64.62% to 68.62% with 261 passing tests.
- Raised `developer.py` coverage from 0% to 74%.
- Kept the Quality Scale tier at Bronze because the Silver coverage threshold remains unmet.

### Quality Scale Bronze
- Added executable behavioural coverage for all config-flow outcomes, including setup success, error mapping, duplicate prevention, gateway selection, reauthentication, reconfiguration, and options safety.
- Strengthened the Quality Scale engine so Bronze requires the dedicated tests and structured coverage evidence rather than keyword detection.
- Promoted the self-assessed Quality Scale level from Legacy to Bronze while preserving all independent target and release gates.

### Pending before 1.1.0 Stable
- Complete clean-install and supported-upgrade validation.
- Validate setup, reload, unload and restart on the declared Home Assistant 2026.x matrix.
- Confirm no duplicate devices or entities and no accidental gate execution.
- Retain the verified Alexa bridge behavior.
- Validate Google Assistant on a real account/device or mark it explicitly unverified.
- Complete HACS, hassfest, Python, JSON and regression gates.

## [1.1.0-rc.15] - 2026-07-22

### Phase 1 — Repository Governance and Integrity Foundation
- Added the Project Governance Charter, Repository Integrity Suite, Roadmap Integrity Check, Definition of Ready/Done, and Zero Knowledge Loss continuity controls.
- Corrected the duplicate roadmap identifier: Documentation Platform moved from 4.3 to 4.4.
- Added ADR-0042 through ADR-0045 and expanded release continuity evidence.

### Phase 2 — Architecture Foundation
- Established the canonical architecture documentation set.
- Added configuration-entry, device, event, data-flow, notification, and module-boundary contracts.
- Added ADR-0046 and ADR-0047.
- Added blocking Architecture Integrity and Mermaid Validation gates.

### Phase 3 — Ecosystem Foundation
- Replaced ecosystem placeholders with canonical product-family contracts.
- Added the normative ecosystem support matrix and capability, adapter, discovery, and identity models.
- Added ADR-0048 and ADR-0049.
- Added the blocking Ecosystem Integrity gate and regression tests.

### Phase 4 — AI Platform Foundation
- Replaced the minimal AI overview with a canonical provider-neutral documentation set.
- Added capability routing, provider interface, policy, privacy, vision, voice, OCR, recognition, automation, and observability contracts.
- Added ADR-0050 through ADR-0053.
- Added the release-blocking `ai_documentation` and `provider_capability` integrity gates.
- No provider adapter or new AI runtime service is claimed as implemented.

### Phase 5 — API Foundation
- Expanded the canonical API reference for entities, registered actions, events, errors, versioning, and security.
- Documented Alexa, Alexa+, and Google Assistant exposure boundaries and automation examples.
- Added ADR-0054 through ADR-0056.
- Strengthened API integrity and added the voice-assistant API gate.
- REST and WebSocket remain contract-only and are not claimed as implemented.

### Governance
- Replaced the placeholder `PROJECT_GOVERNANCE.md` with the canonical governance model covering roles, decision authority, acceptance criteria, release promotion, compatibility, deprecation, document precedence and governance changes.
- Linked governance to the Foundation, official roadmap, ADR register, repository policy, contribution workflow, security policy and release checklist without duplicating their specialist rules.

### Runtime
- Applied the central support-data sanitization policy to native Home Assistant diagnostics. SIP URIs, private IP addresses, persistent identifiers, certificate paths and credentials are now masked or redacted before export.
- Added regression coverage for native diagnostics privacy.
- No other intentional production runtime behavior change beyond release metadata.

## 1.1.0-rc.14 — Documentation Foundation & Repository Refactoring

- Added DRP 2.0 and PCP 2.0 with a binding Project Execution Contract and complete Recovery Prompt.
- Added repository/document lifecycle policy, release checklist, documentation changelog, architecture/API/install/security/performance references, and compatibility matrices.
- Added multilingual RC.14 release summaries for all six supported locales.
- Added ADR-0037 through ADR-0041.
- Added Documentation Platform as roadmap milestone 4.3.
- Archived superseded monolithic handoff, old roadmap, and old documentation index with compatibility pointers.
- Runtime behavior intentionally unchanged except release version metadata.


## [1.1.0-rc.13] - 2026-07-21

### Added
- BTDoor Platform umbrella vision and module naming.
- Complete 1.x–5.x roadmap with AI Vision 1.9, BTicino/Netatmo 2.x and SDK 3.x.
- Ecosystem, AI, SDK, security, performance and developer documentation.
- ADR-0032 through ADR-0036.

### Changed
- Replaced the superseded 1.1-to-2.0 roadmap with a canonical roadmap index.
- Moved Core Consolidation from 1.9 to 1.10.
- Clarified that 1.9 implements interoperable AI Vision while public provider SDKs arrive in 3.x.

## [1.1.0-rc.12] - 2026-07-21

### Documentation
- Completed monthly Home Assistant 2026.x compatibility exposure.
- Added feature recovery and future evolution audit.
- Corrected roadmap treatment of limited call rejection and Call Journal maintenance.
- Archived superseded and provisional-version documents.
- Consolidated historical Foundation ADRs under ADR-0031.
- Expanded and reviewed EN/IT/FR/DE/ES/NL documentation.
- Audited translation key and placeholder parity.
- Added an explicit archive policy and current-document index.

### Runtime
- No functional runtime changes.

This changelog presents BTDoor Security+ as one continuous product line. Early internal packages used experimental 3.x–6.x numbers; those labels are retained only in the provenance register and Git history. They are not separate products and are not supported as a parallel release line.

## [1.1.0-rc.10] - 2026-07-21

### Documentation and engineering governance
- Reconstructed the project history as a single 1.0 Foundation → 1.1 Core Stable product line.
- Added a provenance register mapping historical build labels to current milestones without rewriting Git history.
- Replaced the fragmented changelog with a consolidated product changelog.
- Expanded the architecture, compatibility, quality, release, ADR and engineering-notebook documentation.
- Added a software-archaeology audit identifying implemented, partial, undocumented and deferred capabilities.
- Defined Home Assistant 2026.x compatibility evidence levels.
- Replaced placeholder documentation gates with content and stale-marker checks.

### Runtime
- No intentional runtime or entity-contract change from 1.1.0-rc.8.

## [1.1.0-rc.8] - 2026-07-21
- Restored the approved 1.1–2.0 roadmap, continuity documents and complete handoff.
- Preserved the RC.7 gate button, dedicated voice bridge and Support Bundle behavior.

## [1.1.0-rc.7] - 2026-07-21
- Separated the Alexa/Google gate switch into the dedicated `Alexa / Google Gate Bridge` logical device.
- Preserved stable identifiers, user names and areas.
- Confirmed Alexa discovery and real operation.

## [1.1.0-rc.6b] - 2026-07-21
- Expanded sanitized Support Bundle registry evidence for devices and entities.

## [1.1.0-rc.6a] - 2026-07-21
- Added the optional voice-assistant bridge switch while retaining the native gate button.

## [1.1.0-rc.6] - 2026-07-21
- Established `button.apri_cancello` as the native Home Assistant gate action.
- Removed the temporary cover-based gate contract.

## [1.0.0] - Reconstructed foundation baseline

### Core integration
- Config-entry lifecycle, Cloud runtime, SIP/TLS client, gate command and runtime isolation.
- Stable configuration domain and migration from earlier experimental naming.
- Async-safe diagnostics and filesystem access.

### Observability and support
- Structured diagnostics, Health Score, persistent runtime snapshots and Support Bundle v2.
- Central privacy sanitizer, stable artifact naming and certificate-health isolation.
- Developer Toolkit, runtime inspector, event monitor, metrics and support-report actions.

### Calls and media
- Normalized SIP caller identity, deterministic dialog state, event-driven call journal and call summaries.
- SDP/audio/video offer inspection, codec selection, SRTP metadata and retained media-session diagnostics.

### Home Assistant model
- Stable entity identities, logical device topology, `DeviceKind`, registry-aware naming and visibility.
- Dashboard entity resolution, operations/runtime dashboards and automation blueprints.
- Runtime event bus and dispatcher with per-config-entry ownership.

### Voice and safety foundation
- Audited gate service, Assist sentences, explicit multi-gateway targeting and correlated action events.
- No blind retry for physical gate actions; private exports and sanitized diagnostics.

## Historical provenance
Detailed mappings from experimental labels such as `4.0.0-alpha.*`, `5.0.0-beta.*`, `6.0.*` and `6.1.0-*` are recorded in `docs/release/HISTORICAL_PROVENANCE.md`. Those labels identify development checkpoints, not separate current release families.

## Governance and continuation package

- Added the Project Constitution, official gated workflow, Definition of Ready and Definition of Done.
- Added permanent Engineering Notebook, Translation Review, documented Quality Review, Security and Benchmark governance.
- Added automation/blueprint/Lovelace documentation policy and Final Release HACS/GitHub publication validation runbooks.
- Rebuilt the handoff index, recovery prompt and immediate resume instructions for zero-knowledge-loss continuation.
- Did not alter the approved roadmap points in `docs/roadmap/`.

## Governance Automation Framework

- Added executable governance, handoff and release-readiness checks.
- Added evidence-adjusted Health Score and Governance Compliance Score generation.
- Added consolidated governance automation reporting.
- Added the mandatory GitHub Actions governance workflow.
- Added regression tests for the Phase 6A automation framework.

## Phase 6C — Quality and Release Intelligence

- Added canonical evidence, risk, technical debt and decision traceability registries.
- Added automated evidence consistency and release decision engines.
- Added an explainable Release Decision Report; 1.1.0 Final remains blocked until mandatory runtime, security, compatibility, accessibility and publication evidence is validated.
- Integrated Quality and Release Intelligence into governance automation and repository canonicalization.

## Phase 6D — Runtime and Release Certification

- Added reproducible repository-local runtime, compatibility, security and UX/accessibility certification.
- Added explicit target-runtime and HACS lifecycle blockers.
- Integrated certification into governance automation and release evidence.

## Phase 6F — Release Pipeline & Distribution

- Added reproducible candidate artifact generation.
- Added SHA-256 checksums and machine-readable release manifests.
- Added publication readiness checks tied to certification and release-decision gates.
- Added archive integrity and inventory verification.

### Phase 7B - Home Assistant Certification Enablement

- Added an executable certification harness for real Home Assistant 2026.x targets.
- Added evidence rules, execution runbook, live-target status and an export bridge to the Target Validation Pack.
- Added governance and regression checks that prevent repository-only tests from being represented as live runtime certification.

### Phase 7C - Home Assistant Quality Scale Gate
- Added official-rule-aligned Bronze/Silver/Gold/Platinum self-assessment.
- Added generated `quality_scale.yaml`, JSON/Markdown reports and a blocking Bronze release gate.
- Added conservative handling for exemptions and rules requiring measured/runtime evidence.

### QS-1 - Silver Coverage Program
- Added behavioural tests for runtime summary, visibility policy, and dashboard manager paths.
- Increased measured integration coverage from 34.27% to 35.54%.
- Prevented coverage measurement from creating `.pytest_cache` and invalidating repository-integrity checks.
- Added coverage priority map, ADR-0069, and handoff 42.
- Silver remains blocked pending measured coverage above 95%.

### QS-3 - Sensor Platform Coverage
- Added behavioural coverage for every public sensor entity, setup modes, listeners, API fallbacks, and branch variants.
- Raised `sensor.py` coverage to 98.74% and total measured integration coverage from 40.59% to 53.24%.
- Added ADR-0071, QS-3 coverage report, and handoff 44.
- Silver remains blocked pending total measured coverage above 95%.

### QS-4 - Services and Cloud Coverage
- Added executable behavioural tests for global service registration, targeting, success/failure handling, developer actions, and call-journal operations.
- Added executable coverage for MyHomeWeb authentication classification, parsing, gateway discovery, SIP-user reuse/creation, identity helpers, and certificate-file handling.
- Increased measured integration coverage from 53.24% to 59.24%; 253 tests pass.
- Added ADR-0072, the QS-4 coverage report, and handoff 45.
- Silver remains blocked pending total measured coverage above 95%.

### QS-7 Lifecycle and SIP Transport Coverage

- Added behavioural SIP lifecycle and transport tests.
- Increased cumulative measured integration coverage from 68.62% to 71.57%.
- Increased `sip_client.py` coverage from 40.02% to 53.95%.
- Added ADR-0075, QS-7 report and handoff 48.
- Quality Scale remains Bronze; Silver remains blocked by the >95% coverage requirement.

### QS-9 - Runtime, Support and Voice Coverage
- Added behavioural coverage for runtime data, support-debug redaction and persistence, managed Assist sentences, and native voice intents.
- Increased measured integration coverage from 73.49% to 76.56%.
- Raised `runtime.py`, `sentence_manager.py`, and `voice.py` to 100%; `support_debug.py` to 94%.
- Added ADR-0077, QS-9 coverage report, and handoff 50.
- Silver remains blocked pending total measured coverage above 95%.

### QS-10 - Device Registry and Journal Coverage
- Added behavioural coverage for device visibility cleanup, registry creation, metadata migration, localized reporting and topology validation.
- Added Call Journal coverage for load/self-healing, event lifecycle, media metadata, metrics, rebuild and clearing.
- Increased measured integration coverage from 76.56% to 79.23%.
- Raised `device_model/manager.py` to 100%, `managers/device_manager.py` to 85%, and `call_journal/journal.py` to 94%.
- Added ADR-0078, the QS-10 coverage report, and handoff 51.
- Silver remains blocked pending total measured coverage above 95%.

### QS-12 — Cloud and SIP Dispatch Coverage

- Added behavioural cloud transport and SIP request/response dispatch tests.
- Increased measured integration coverage from 80.49% to 83.22%.
- Kept Silver blocked until coverage exceeds 95%.

### QS-22 — Platinum Readiness Audit

- Completed a documentation-only audit of the three Home Assistant Platinum rules.
- Confirmed Home Assistant shared aiohttp session injection in all identified cloud-client construction paths.
- Identified the missing external async communication dependency as the primary architectural blocker.
- Measured the strict-typing baseline and documented the remaining `ConfigEntry[Any]`, annotation, and `Any` debt.
- Added async lifecycle, public API, dependency, WebSession, strict typing, and implementation-plan reports under `docs/platinum/`.
- Kept the Quality Scale self-assessment at Gold; no runtime implementation or Platinum promotion was performed.

### QS-23 — Gold Project Policy

- Adopted Quality Scale Gold as the permanent project target, release minimum and maximum governed tier.
- Added strict workflow enforcement that blocks advancement on any Gold regression or silent policy change.
- Removed Platinum rules from active remediation while retaining informational assessment.
- Added Gold policy tests, ADR-0090, QS-23 report and handoff 64.
- Updated workflow, roadmap, README and canonical Quality Scale documentation.

## Governance consolidation — Documentation and Localization

- Added RG-001 through RG-004 as the authoritative governance rule registry.
- Added the Project Governance System, Framework Registry, Document Impact Matrix and Workflow Compliance Matrix.
- Added an executable Localization Framework covering every shipped integration locale.
- Removed the duplicated workflow body from the handoff layer and retained the project workflow as the single source of truth.
- Added a reproducible documentation consolidation audit.

## RC15 pre-Phase 7C repository hygiene

- completed the mandatory bootstrap and repository-wide governance audit;
- removed transient `.coverage`, Python caches and empty validation work directories from the canonical package;
- moved the nested RC15 release ZIP and checksum to a separate companion archive;
- retained the structured release JSON and historical Platinum audit trail without treating Platinum as an active governed tier;
- documented that GOLD and Release Readiness pass while the Release Decision Engine remains BLOCKED.

## Unreleased — Phase 7C GitHub sandbox validation remediation

### Governance
- Added the permanent GitHub Sandbox Validation Gate for every RC and Final release.
- Required a clean GitHub-hosted sandbox using Python 3.13, the latest stable official Ruff release, and all repository release validators.
- Prohibited weakening Ruff rules or reducing the required Home Assistant Integration Quality Scale level to obtain release approval.

### CI and validation
- Added `.github/workflows/github-sandbox-validation.yml` as the read-only mandatory validation workflow.
- Added `.github/workflows/ruff-remediation.yml` as a manually dispatched remediation workflow that applies Ruff fixes and commits only after the complete validation suite passes.
- Added `tools/validation/github_sandbox_validate.sh` to provide the canonical sandbox validation sequence and versioned evidence.

### Documentation
- Added ADR-0091 and the GitHub Sandbox Validation operational guide.
- Updated governance, quality gates, document impact, engineering notebook and handoff continuity records.

### GitHub validation remediation update - 2026-07-27

- Corrected the GitHub Home Assistant compatibility matrix so Home Assistant 2026.3-2026.7 runs on Python 3.14.2 while 2026.1 retains Python 3.13.
- Updated the GitHub sandbox and Ruff remediation workflows to use Python 3.14.2 and current GitHub Actions.
- Reworked Ruff remediation so safe mechanical fixes are committed even when semantic residual findings remain; residual reports are preserved as mandatory evidence and still block compliance.
- Added optional explicit unsafe-fix execution without weakening the read-only release validation gate.
- Release status remains blocked until the follow-up GitHub validation run is fully green and GOLD evidence is preserved.
