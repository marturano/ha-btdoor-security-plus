# Phase 7C — Runtime Lifecycle Hardening

**Date:** 2026-07-23  
**Package:** `1.1.0-rc.15-phase7c-runtime-hardening`  
**Roadmap phase:** Phase 7C — Release Candidate Approval  
**Runtime delta:** lifecycle cleanup and SIP task shutdown hardening  
**Decision:** **BLOCKED — target and external evidence still required**

## Scope

This iteration performs a focused code review against the authoritative Phase 7C workflow. It adds no feature and does not authorize Phase 7D. The review concentrates on resources allocated during config-entry setup and on deterministic shutdown of SIP background tasks.

## Verified findings and remediation

### RH-7C-001 — Setup-failure resource leak

The integration started the support-debug writer before certificate renewal and SIP setup. If setup then failed, Home Assistant would not call `async_unload_entry` for the never-loaded entry, leaving the debug task and, in later failure paths, SIP resources active.

**Remediation:**

- stop the debug recorder when certificate renewal fails;
- stop the SIP client and debug recorder when SIP startup fails;
- introduce `_async_cleanup_runtime()` as the shared cleanup path;
- invoke cleanup when device registration or platform forwarding fails;
- reuse the same cleanup path during normal unload.

### RH-7C-002 — Call-timeout task cancelled without awaiting completion

`BticinoSipClient.async_stop()` cancelled `_call_timeout_task` but did not await it. This could leave a pending-task warning or incomplete cancellation during reload and shutdown.

**Remediation:** cancel and await the task, suppressing only the expected `asyncio.CancelledError`, before clearing the task reference.

## Regression tests

Added behavioural tests verifying that:

- setup cleanup unsubscribes renewal and event listeners;
- SIP and debug resources are awaited during cleanup;
- the call-timeout task is cancelled, awaited and cleared.

## Verification

| Verification | Result |
|---|---|
| Focused lifecycle and setup orchestration tests | PASS — 10 tests |
| Complete repository test suite with cache and third-party plugin isolation | PASS — 332 tests |
| Python bytecode compilation | PASS |
| Runtime feature scope | unchanged |
| Release Decision Engine | remains BLOCKED |
| Ruff static analysis | NOT EXECUTED — module unavailable in runner |

The authoritative complete-suite command used cache suppression and disabled unrelated auto-loaded pytest plugins so the runner terminated cleanly:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider -p pytest_asyncio.plugin
```

## Phase 7C status

The runtime is hardened, but Phase 7C remains active and blocked by the established target/external evidence and the exact-package Ruff result. Phase 7D is not authorized.
