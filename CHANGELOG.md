# 6.0.0

- Promoted the validated 6.0.0-rc.3g code to the first stable 6.0 release.
- Preserved all device identifiers, entity identifiers, user-assigned names, areas, and device associations.
- Confirmed localized Italian Device Registry names for Cloud and SIP logical devices.
- Aligned package and device software metadata to 6.0.0.
- No runtime, configuration, service, entity, or feature changes from 6.0.0-rc.3g.

# 6.0.0-rc.3g

- Corrected the Italian Device Registry names for Cloud and SIP logical devices.
- Aligned the device `sw_version` metadata with the package version.
- Preserved all existing device identifiers, entity identifiers, user-assigned names, areas, and device associations.
- No new features; the 6.0 feature freeze remains in effect.

# 6.0.0-rc.3f

- Added an explicit Device Registry migration that updates integration-managed logical-device names while preserving user-defined names.
- Added `registry/devices.json` to Support Bundles with expected and effective device names.
- Added `translations/report.json` with Home Assistant language, resolved language, fallback state, and localized logical-device names.
- Standardized registry manufacturer, model, and software version metadata during migration.

# 6.0.0-rc.3d

- Fixed Support Bundle generation after the DeveloperTools entry attribute refactor.
- Standardized English device terminology: Cloud Status, SIP Monitor, Call Manager, Multimedia Monitor, and Advanced Diagnostics.
- Aligned Italian, French, German, and Spanish option labels with the canonical English glossary.
- Corrected remaining untranslated English service text.

# 6.0.0-rc.3b — Circular import hotfix

- Eliminated the circular import between `visibility` and `device_model`.
- Made `device_model.async_register_devices` a lazy wrapper so importing the package no longer imports the registry lifecycle manager.
- Preserved the existing device visibility behavior and registry cleanup logic.
- Added regression coverage for importing `visibility`, `device_model`, and `developer` in the same process.

# 6.0.0-rc.3a — Import optimization hotfix

- Reduced package-level imports in `__init__.py` to lightweight constants and Home Assistant interfaces.
- Deferred SIP, cloud, cryptography, media, diagnostics, event-bus and journal imports until config-entry setup or unload.
- Moved the initial certificate file existence check to `asyncio.to_thread`.
- Added a regression test that prevents expensive integration subsystems from being imported at package load time.
- No entity, service, device-visibility or runtime behavior changes.

# 6.0.0-rc.3

- Renamed logical devices to Cloud Status, SIP Monitor, Monitor Chiamate, Media Monitor and Diagnostica Avanzata.
- Added per-module visibility options with a clear description beneath every option.
- Added the central Device Visibility Manager used by platforms and the Device Registry lifecycle.
- Hidden modules now remove their entities and logical device while the internal runtime continues operating.
- Diagnostica Avanzata requires both its visibility option and Developer mode.
- Added effective visibility settings to `configuration/options.json` in Support Bundles.

## 6.0.0-rc.3e

- Localized logical device names using the active Home Assistant language.
- Added automatic English fallback for unsupported locales.
- Added Dutch device-name terminology in preparation for the 6.1 language framework.
- Added an in-place Device Registry migration that preserves device IDs, entities, areas, history, and user-assigned names.
- Added regression tests for Italian names, locale normalization, and fallback behavior.

## 6.0.0-rc.3 — Central export sanitizer

- Added a single export sanitization policy in `support_sanitizer.py`.
- Standard Support Bundles now hash `entry_id`, `config_entry_id`, `device_id`, SIP correlation identifiers and partially mask `gateway_id`.
- Credentials, tokens, private keys, certificates and cryptographic material are always removed.
- All structured Support Bundle payloads continue to pass through `sanitize_support_data`, which now delegates to the central sanitizer.
- Added regression coverage for recursive sanitization, deterministic correlation hashes and gateway masking.

## 6.0.0-rc.2c — Call summary device assignment

- Moved the `Last call summary` (`Riepilogo ultima chiamata`) sensor from `Media Monitor` to `Monitor Chiamate`.
- Preserved the sensor unique ID and entity ID so existing dashboards, automations, history, and statistics continue to work.
- Kept media-specific codec and close-reason attributes available on the call summary while assigning the entity to the call-management device.
- Updated the device-topology and Operations Dashboard documentation.

## 6.0.0-rc.2b — Naming and Developer Mode lifecycle

- Renamed the configuration entry to `Bticino DS+ Suite`.
- Renamed logical runtime devices to `Cloud Status`, `Diagnostica Avanzata`, `Monitor Chiamate`, `Media Monitor`, and `SIP Monitor`.
- Developer Mode now exclusively controls the `Diagnostica Avanzata` device and all of its entities. Disabling Developer Mode removes the diagnostic entities and device from the Home Assistant registries; enabling it recreates them on reload.
- Updated user and engineering documentation for the new naming and Developer Mode lifecycle.

- Fixed `Developer Runtime Inspector` startup by serializing the complete `RuntimeSnapshot` through its supported `as_dict()` method.
- Removed invalid calls to `as_dict()` on nested state dataclasses such as `GatewayState`.
- Added a regression check that forbids nested runtime state `.as_dict()` calls in the Developer sensor.
- Preserved all entity unique IDs, options and runtime storage.

## 6.0.0-rc.2

- Expanded Developer Mode with three diagnostic entities: Runtime Inspector, Event Monitor, and Event Metrics.
- Developer Event Monitor exposes a sanitized 20-event timeline without raw SIP payloads.
- Developer Runtime Inspector uses immutable RuntimeStateProvider snapshots.
- Developer Mode remains disabled by default and is applied through the Config Entry options reload.

# Changelog

## 6.0.0-rc.1a — Service registration hotfix

- Fixed integration startup on Home Assistant 2026.7 by removing the accidental extra positional `INTEGRATION_VERSION` argument from four `ServiceRegistry.async_register()` calls.
- Ensured each service schema is passed exactly once.
- Reused the central integration version constant in the Device Model instead of the stale `5.0.0-beta.4` marker.
- Preserved entity unique IDs, storage keys, Config Entries, Event Bus and Call Journal data.

## 6.0.0-rc.1 — Production-readiness foundation

- Promoted the validated 5.1 runtime architecture to the first 6.0 release candidate.
- Added a single `INTEGRATION_VERSION` runtime constant and removed stale hard-coded beta version markers.
- Hardened structured SIP diagnostic redaction for standalone tag, instance, Call-ID and branch fields.
- Added HACS and Hassfest validation workflows.
- Added automated Python compile, JSON validation and pytest workflow steps.
- Added a deterministic GitHub release-package workflow.
- Added Ruff, mypy and pytest project configuration.
- Added repository contribution, security, issue-template and pull-request documentation.
- Added an explicit quality/readiness matrix without claiming unverified Home Assistant Quality Scale status.
- Reworked the README for HACS installation, operations, voice-assistant exposure and release-candidate expectations.
- Preserved all entity unique IDs, storage keys and configuration-entry behavior.

## 5.1.0-beta.2

- Fixed stale active-call accounting through deterministic journal rebuild/clear support.
- Added canonical SDP and media allocation event types to reduce generic runtime events.
- Added clear, export and rebuild Call Journal services.
- Added average duration, answered today and missed today sensors.


## 5.1.0-beta.2.1

- Fixed `active_calls` inflation caused by late duplicate terminal events after `media_closed`.
- Added storage self-healing for completed records incorrectly persisted in the active map.
- Prevented terminal and auxiliary events from creating phantom active calls.
- Normalized `media_srtp_selected`, `media_local_sdp_generated`, and `sdp_offer_parsed`.
- Added regression coverage for duplicate `missed_call` events and persisted-state migration.

## 5.1.0-beta.2

- Added a persistent Call Journal derived exclusively from normalized Runtime Event Bus events.
- Retains the latest 250 completed calls with result, caller, duration, codecs, SRTP suite and close reason.
- Added journal metrics and three Home Assistant sensors for latest call, retained calls and missed calls.
- Added `calls/journal.json`, `calls/metrics.json` and `calls/schema.json` to Support Bundles.
- Preserved all existing entity unique IDs and runtime behavior.

## 5.0.0-beta.4 - Runtime Event Framework

- Added a per-config-entry, versioned Runtime Event Bus.
- Added immutable RuntimeEvent models with stable schema version 1.
- Normalized existing SIP, dialog, media, cloud and gate notifications.
- Added bounded persistent history for the latest 500 runtime events.
- Added event metrics grouped by event type and logical source.
- Exported event history, metrics and schema metadata in Support Bundles.
- Preserved the public Home Assistant event bus for backward compatibility.

## 5.0.0-beta.3

- Added the Operations Center foundation.
- Added `sensor.operations_summary` backed by the stable Runtime State Provider.
- Added a provider-neutral `RuntimeSummary` model for future dashboard, Repairs and AI consumers.
- Added a native Lovelace dashboard template in `dashboards/btdoor_operations.yaml`.
- Preserved all existing entity unique IDs.


## 5.0.0-beta.1 — Runtime State Provider

- Added immutable gateway, cloud, SIP, dialog, media and diagnostics state models.
- Added `RuntimeStateProvider` as the single normalized read path for runtime data.
- Added the stable internal `BTDoorRuntimeAPI` facade for entities, diagnostics, services and future AI consumers.
- Migrated alpha.30 observability entities to the new facade while preserving entity unique IDs and compatibility fallbacks.
- Added structured snapshot serialization and Beta.1 regression tests.
- Added ADR-0018 and updated architecture documentation.

## 4.0.0-alpha.29

- Fixed Media Runtime snapshots disappearing after an integration reload or Home Assistant restart.
- Persisted the last completed media session, the bounded 10-session history and aggregate metrics.
- Persisted redacted SDP diagnostics, media trace metadata and SIP dispatcher counters.
- Restored integration state before starting the SIP transport.
- Made media finalization idempotent so an already closed session is not added twice.
- Added ADR-0016 and regression coverage for close, export and restore lifecycle behavior.

## 4.0.0-alpha.26 — Persistent Runtime Snapshot

- Added a bounded history of the last 10 completed media sessions.
- Preserved the last completed media plan, trace, SDP availability, duration, and close reason after the live runtime returns to an inactive state.
- Added aggregate media metrics for codec usage, close reasons, retained sessions, and average duration.
- Added dedicated Support Bundle exports for the last completed session, session history, and metrics.
- Added regression tests for persistent media diagnostics.

## 4.0.0-alpha.24 — Certificate Migration & Diagnostic Health

- Added certificate migration from the former `btdoor_entry_plus` storage paths after the domain rename.
- Aligned Developer certificate diagnostics with the exact paths used by the live SIP client.
- Made the aggregate Health test non-raising and independent, preventing certificate failures from cascading into false TLS/health failures.
- Added explicit `tls_runtime` and certificate status details to health diagnostics.
- Updated the setup debug version marker to `4.0.0-alpha.24`.
- Added ADR-0011 and regression coverage for legacy certificate-path migration and health isolation.

## 4.0.0-alpha.22 — Support Identity Migration

- Renamed generated support artifacts to `BTDoorSecurityPlus_Support_<timestamp>.md/.zip`.
- Updated support retention to manage both the new prefix and legacy `BTDoorPlus_Support` / `BTDoorEntryPlus_Support` files safely.
- Kept cleanup backward compatible so existing reports do not cause errors after the rename.
- Added centralized support-artifact naming helpers and regression tests.
- Updated the SDP origin label from `BTDoorPlus` to `BTDoorSecurityPlus`.
- Added ADR-0009 documenting support artifact naming and legacy compatibility.

## 4.0.0-alpha.21 — Async Compliance

- Fixed the Home Assistant blocking-call warning raised while generating a support report on Python 3.14.
- Moved `platform.platform()` collection to a worker thread before building the in-memory support snapshot.
- Moved SIP certificate existence checks off the event loop.
- Moved certificate migration and renewal fallback filesystem checks off the event loop.
- Added ADR-0008 documenting the async-compliance policy.

## 4.0.0-alpha.20 — Foundation

- Renamed the project to **BTDoor Security+**.
- Changed the Home Assistant domain to `btdoor_security_plus` (breaking alpha migration).
- Added the device-neutral Platform Core and lifecycle orchestration.
- Added the `DeviceAdapter` capability contract.
- Added the first deterministic SIP Dialog Engine and tests.
- Added architecture, ADR-0007, migration guide, and Engineering Notebook.

## 4.0.0-alpha.20 — SIP Dispatcher Instrumentation

- Added bounded packet-by-packet SIP dispatcher tracing.
- Added INVITE counters: received, dispatched, with SDP, and with Media Runtime.
- Added dispatcher stage records around request parsing, branch selection, SDP detection, and Media Runtime invocation.
- Added `sip/dispatcher_trace.json` to Support Bundles.
- Added dispatcher diagnostics to Home Assistant diagnostics and Developer Tests.
- No call acceptance, RTP, RTCP, or SRTP transmission is enabled.

## 4.0.0-alpha.18 — Media Runtime Instrumentation

- Added per-INVITE Media Trace IDs (`MT-xxxxxx`).
- Added step-by-step instrumentation from INVITE reception to runtime storage.
- Added explicit trace records for SDP extraction, parsing, media preparation and snapshot storage.
- Added `media/instrumentation.json` to Support Bundles.
- Added Media Runtime instrumentation to diagnostics and Developer Tests.
- No SIP call acceptance or RTP/SRTP transmission is enabled.

## 4.0.0-alpha.17

- Added persistent Media Runtime lifecycle (`idle`, `preparing`, `prepared`, `failed`, `closed`).
- Preserves an export-safe media snapshot after RTP sockets and SRTP keys are released.
- Added media timeline events and Media Engine health check.
- Added remote SDP, redacted local SDP, SDP diff and media runtime files to support bundles.
- Media diagnostic entities now retain the last session state after CANCEL/BYE.
- Calls are still not accepted and no RTP/SRTP traffic is transmitted.

## 4.0.0-alpha.16

- Added strict SDES-SRTP inline key parsing and 30-byte master key validation.
- Added local media address discovery.
- Added in-memory SDP answer generation with export-safe redacted preview.
- Added SRTP key lengths, local crypto tag, SDP fingerprint and preparation timestamp to diagnostics.
- The SIP call is still not accepted and no RTP/SRTP packets are transmitted.

## 4.0.0-alpha.15

- Fixed the remaining X.509 long Common Name warning by filtering it while reading certificate subject and issuer.
- Confirmed Developer Test and Support Report remain operational.

## 4.0.0-alpha.14

- Fixed the X.509 long Common Name warning in Developer Test.
- Clarified that the SIP message counter includes only incoming SIP MESSAGE requests.
- Clarified that the reconnection counter includes only real successful SIP reconnections.
- Added counter scope metadata to diagnostics.
- Updated IT/EN/FR/ES/DE counter names and descriptions.

## 4.0.0-alpha.13

- Added non-invasive Media Engine preparation.
- Added SDES-SRTP crypto parsing without exporting key material.
- Added local RTP/RTCP port reservation during an incoming offer.
- Added preferred codec selection and diagnostic sensors.
- No SIP 200/SDP answer or media transmission is enabled yet.

## 4.0.0-alpha.12

- Refactored support diagnostics around structured, typed Python data.
- Support JSON is now sanitized before serialization; regex is never applied to a serialized JSON document.
- SIP From, To and Contact headers are normalized into structured objects for support exports.
- Fixed quote corruption around SIP tags and `+sip.instance` values.
- JSONL logs are parsed and sanitized record by record.
- Added regression tests and a standalone support-bundle JSON validator.

## 4.0.0-alpha.11

- Fixed Developer Mode button entity category for Home Assistant 2026.7.
- Replaced the remaining string value `"diagnostic"` with `EntityCategory.DIAGNOSTIC`.
- Audited the integration for other invalid entity category assignments.

## 4.0.0-alpha.10

- Fixed Developer Mode button entities for Home Assistant 2026.7 by using `EntityCategory.DIAGNOSTIC`.
- Fixed support report generation: redaction now operates recursively on structured data before JSON serialization.
- Prevented `JSONDecodeError` while generating Markdown and debug bundles.

## 4.0.0-alpha.9

- Support report Markdown now uses the fully support-sanitized dataset.
- SIP Call-ID, branch, tags, sip.instance and IPv4 addresses are masked in exported reports.
- Statistics reset now clears reconnect count, command timestamps and persisted SIP timeline.
- Added current runtime session identifiers and separate current/historical SIP timelines.
- Added non-invasive Health Check with weighted score and issue list.
- Support bundle now exports separate current-session and historical timelines.

# Changelog

## 4.0.0-alpha.9

- Spostati log e report sotto `custom_components/btdoor_security_plus`.
- Migrazione automatica dei dati diagnostici legacy.
- Rotazione log 5 x 5 MB e retention massima di 20 report.
- Sanitizzazione obbligatoria delle chiavi SRTP SDES e anonimizzazione IP nei bundle esportati.
- Corretto il falso reconnect della sessione SIP inattiva.
- Gestione SIP CANCEL completa: `200 OK` al CANCEL e `487 Request Terminated` all'INVITE con lo stesso To-tag.
- Aggiunti pulsante e servizio `clean_debug_environment`.
- Roadmap aggiornata con Developer Platform, Self Diagnostic Engine, SRTP e BTDoor AI.

## 4.0.0-alpha.7

- Added visible Developer Mode buttons and status sensors.
- Fixed diagnostic SIP tests changing `registered` to false.
- Fixed idle reader timeout causing artificial reconnects.
- Report version now comes from the installed integration manifest.
- Added detailed SDP fmtp/protocol/payload data, dialog headers and SIP timeline.
- Added sanitized SDP/dialog/timeline files to support bundles.

## 4.0.0-alpha.6

- Fixed malformed Home Assistant service registration that prevented config entry setup.
- Registered reject_call, developer_test, generate_support_report and export_debug_bundle as separate services with the correct schemas.

## 4.0.0-alpha.6

- Added retries for transient MyHomeWeb disconnections during binary certificate provisioning.
- Existing valid certificate files no longer block integration startup when cloud renewal temporarily fails.
- Missing certificate material still triggers Home Assistant retry behavior.

# 4.0.0-alpha.4

- Complete Developer Mode with safe Cloud/TLS/SIP/certificate/SDP/dialog tests.
- Generate Support Report action producing redacted Markdown and ZIP bundles.
- Developer mode option separated from Support Debug.

## 4.0.0-alpha.3

- Added Support Debug options flow (Off, Support, Deep Debug).
- Added redacted asynchronous rotating JSONL diagnostics.
- Added sanitized SIP protocol frame logging in Deep Debug.
- Added recent support records to Home Assistant diagnostics.
- Logs are stored under `/config/btdoor_security_plus/logs/<entry_id>/`.

## 4.0.0-alpha.2

- Added SDP parser for session/media connection data.
- Added dynamic and static RTP codec mapping.
- Added audio/video RTP offer diagnostic sensors.
- Added `sdp_offer_parsed` Home Assistant event.
- Calls are still not accepted and RTP is not started.

# Changelog

## 4.0.0-alpha.1
- Avvio Milestone 4 / Fase 4.1.
- Tracciamento stato dialogo SIP e offerta SDP.
- Gestione ACK, INFO, NOTIFY, REFER, SUBSCRIBE, PRACK e UPDATE.
- Nuova azione `btdoor_security_plus.reject_call`.
- Nuovi sensori diagnostici per dialogo, metodo SIP e SDP.

## 3.0.0-alpha.19
- Ultima build funzionante e baseline stabile della Milestone 3.

## 4.0.0-alpha.25 - Diagnostic Framework

- Added a modular asynchronous `DiagnosticProvider` contract.
- Added isolated provider orchestration and weighted, non-cascading health aggregation.
- Added Support Bundle schema 3 with `diagnostics/providers/*.json` and `diagnostics/framework-health.json`.
- Preserved all schema 2 diagnostic files for backward compatibility.
- Removed absolute certificate and private-key paths from exported certificate status.
- Added ADR-0012 and framework unit tests.

## 4.0.0-alpha.27 — Developer Toolkit

- Added dependency-free `validate.py`, `deploy.py`, `reload.py`, `restart.py`, `watch.py`, `logs.py` and `support_bundle.py` tools.
- Added atomic-style component replacement while preserving certificate, log and support data.
- Added REST API automation for config-entry reload, controlled Core restart and support-bundle generation.
- Added change classification in watch mode: metadata reload versus Python/manifest restart.
- Added ADR-0014 and developer workflow documentation.

## 4.0.0-alpha.30 — Home Assistant Observability Entities

- Added a compact **Last call summary** sensor backed by the persisted media session.
- Added last media close reason, runtime health, runtime score and retained media session sensors.
- Added Media ready, Last call missed and Runtime healthy binary sensors.
- Added structured call attributes including caller, Call-ID, duration, codecs and close reason.
- Added pure entity metric helpers and regression tests.
- Added ADR-0017 and multilingual entity names.
- Avoided exposing a synthetic cloud-connected state until a persistent cloud runtime exists.

## 5.0.0-beta.2

- Added a six-device Home Assistant model: Gateway, Cloud, SIP, Dialog, Media, and Diagnostics.
- Added stable central identifiers and a `DeviceInfo` factory.
- Added `via_device` relationships from all logical runtime devices to the physical gateway.
- Preserved the legacy gateway identifier to avoid an orphaned pre-Beta.2 device.
- Reassigned existing entities to their correct logical device without changing entity `unique_id` values.
- Added Device Registry bootstrap during config-entry setup.
- Added ADR-0019 and Beta.2 regression tests.

## 5.0.0-beta.2.1

- Added Cloud Runtime entities: connection, state, endpoint and last error.
- Added Dialog Runtime entities: active call and dialog call ID.
- Extended the runtime state provider with richer cloud state and `devices()`.
- Preserved all existing entity unique IDs.

## 5.0.0-beta.4.1

- Connected the SIP call lifecycle to the Runtime Event Bus with an explicit `invite_received` event.
- Added mappings for the actual media notifications emitted by the runtime: `media_session_prepared` and `media_session_failed`.
- Added setup-time SIP and Cloud synchronization events so registration/authentication state is present even when it completed before the Home Assistant listener was attached.
- Updated event payloads with call identifiers, caller, SDP availability and synchronization metadata.

## 6.0.0-rc.3c

- Added the mandatory complete `translations/en.json` catalog required by current Home Assistant custom-integration localization.
- Restored translated names and per-field descriptions in the options flow.
- Localized Support Debug selector values in English, Italian, German, Spanish, and French.
- Added translation-regression tests for options-flow keys and selector values.
