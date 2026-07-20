# ADR-0016 — Media lifecycle persistence

## Status
Accepted for 4.0.0-alpha.29.

## Context
The SDP summary survived a Home Assistant restart because it was included in the integration store, while the completed Media Runtime snapshot, bounded history, metrics and SIP dispatcher counters existed only in memory. A support bundle generated after a reload therefore showed the last call as missed but exported an empty media history.

The release path could also finalize an already closed runtime again when the next SDP offer was parsed.

## Decision
Persist only export-safe Media Runtime data in the Home Assistant store:

- last detached media plan;
- last completed session;
- bounded session history;
- media timestamps and redacted SDP artifacts;
- media trace metadata and bounded trace;
- SIP dispatcher counters and bounded trace.

Never persist sockets, active key material or unredacted local SDES keys.

Restore persisted state before starting the SIP transport. Finalize sessions only from `preparing`, `prepared` or `failed`; `closed` and `idle` are idempotent no-ops.

## Consequences
Support bundles remain useful after reloads and restarts, session metrics are stable, and repeated cleanup cannot duplicate history entries. The stored payload is larger but bounded by the existing trace and history limits.
