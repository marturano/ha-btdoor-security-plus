# ADR-0008 — Home Assistant Async Compliance

- **Status:** Accepted
- **Version:** 4.0.0-alpha.21

## Context

Home Assistant 2026.7 detects blocking file operations executed on its asyncio event loop. On Python 3.14, `platform.platform()` may open the Python executable while collecting platform metadata, which caused support-report generation to emit a blocking-call warning.

## Decision

All filesystem, certificate, platform-inspection, archive and other potentially blocking operations must run through `asyncio.to_thread()` or Home Assistant's executor facilities. Pure in-memory snapshot assembly remains on the event loop.

## Consequences

- Support report generation no longer invokes `platform.platform()` on the event loop.
- SIP certificate existence checks are delegated to a worker thread.
- Certificate migration and fallback checks avoid synchronous filesystem metadata calls in async paths.
- Future code reviews must treat `Path.exists()`, `Path.is_file()`, `Path.is_dir()`, file reads/writes, archive operations and platform probing as blocking unless proven otherwise.
