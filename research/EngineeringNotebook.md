# BTDoor Security+ Engineering Notebook

## 2026-07-17 — Foundation and namespace reset

The project was renamed before a stable release to avoid carrying a
model-specific identity into the platform architecture. The Home Assistant
domain was changed immediately, accepting a manual alpha migration.

A minimal device-neutral Platform Core, DeviceAdapter contract, and deterministic
Dialog Engine were introduced without replacing the validated cloud and SIP
runtime in the same release. This limits regression risk while establishing the
boundaries required for later RTP, SRTP, audio, video, and Netatmo adapters.


## 2026-07-17 — Python 3.14 blocking-call finding

Home Assistant reported a blocking `open('/usr/local/bin/python3.14', 'rb')` while generating a support report. The integration did not call `open()` directly at that line; Python's `platform.platform()` did so internally. The fix collects platform metadata in `asyncio.to_thread()` and keeps support snapshot construction in memory. A broader pass also moved certificate path metadata checks out of async execution paths.


## 2026-07-17 — Support identity migration (4.0.0-alpha.22)

The support generator still emitted the historical `BTDoorPlus_Support` filename after the domain migration. Naming is now centralized in `support_naming.py`. Retention intentionally recognizes both current and historical prefixes so installations upgraded from earlier alpha builds can keep, rotate, or clean old bundles without exceptions. The ZIP member report uses the same new filename as the external Markdown report.


## 2026-07-17 — alpha.24 certificate migration and health isolation

A support bundle showed valid SIP registration, incoming INVITE traffic, and media preparation while the certificate and TLS developer tests failed on a missing path below the renamed domain. Root cause: the alpha.20 migration did not include the former `btdoor_entry_plus` certificate directory. The fix adds legacy-source discovery, aligns diagnostics with runtime paths, and removes cascading aggregate-health failures.

## 2026-07-17 - 4.0.0-alpha.25 Diagnostic Framework

Introduced a provider-based diagnostic architecture. Existing developer checks are normalized into independent provider results, aggregated with weighted health scoring, and exported using Support Bundle schema 3. Legacy bundle files remain available. Absolute certificate paths are no longer exposed in support exports.

## 2026-07-17 - 4.0.0-alpha.26 Persistent Runtime Snapshot

Media teardown correctly released sockets and SRTP key material, but it also removed the temporal context needed for post-call diagnosis. The runtime now retains sanitized snapshots for the last ten completed sessions, including negotiated codecs, close reason, duration, trace, and SDP availability. Raw SRTP keys remain excluded.

## 2026-07-17 — alpha.27 Developer Toolkit

Introduced a repository-local deployment loop. The key architectural constraint is explicit: config-entry reload is a runtime lifecycle operation, not a Python hot-module loader. The toolkit therefore classifies source changes and preserves a safe restart path while still avoiding restarts for metadata and runtime-only work.


## 2026-07-17 — alpha.29 Media lifecycle persistence

The alpha.28 support bundle retained the parsed SDP summary but lost `last_completed`, history and media metrics after a runtime reload. Root cause: these structures were memory-only, while legacy SDP fields were already included in `export_state()`. Alpha.29 adds bounded export/restore of redacted media diagnostics, restores state before SIP startup, and makes finalization idempotent by accepting only active lifecycle states.

## 2026-07-17 — Alpha.30 native observability entities

Converted the persistent runtime snapshot work into native Home Assistant entities. The key design constraint was to avoid network I/O inside entity properties. Runtime health is therefore calculated from live local facts, while full active diagnostics remain in the provider framework and Support Bundle. A continuous cloud-connected entity was deliberately deferred because the current cloud client is transactional rather than a persistent runtime.


## 2026-07-17 — 5.0.0-beta.1

Introduced the immutable Runtime State Provider and stable internal API. The first consumers are the alpha.30 observability entities. Compatibility paths are intentionally retained while remaining direct runtime readers are migrated incrementally. This establishes the schema boundary required for the future Device Model, dashboard, services and AI diagnostics.

## 2026-07-17 — 5.0.0-beta.2 Device Model

Implemented the Home Assistant Device Registry hierarchy. The physical gateway is the root. Cloud, SIP, Dialog, Media, and Diagnostics are modeled as child service devices through `via_device`. The legacy `sip_client_<id_device>` identifier is retained on the gateway to let Home Assistant merge the old device record. Existing entity unique IDs are unchanged.

## 5.0.0-beta.2.1 - Device Model completion

Cloud Runtime and Dialog Runtime now expose native Home Assistant entities, so no logical runtime device is intentionally empty. Existing unique IDs remain unchanged.
