# Async Dependency Audit

> **Document status:** Historical / informational  
> **Normative:** No  
> **Active roadmap scope:** Excluded  
> **Current policy:** GOLD is the permanent governed maximum. This document is retained only as historical engineering evidence.


## Finding

The implementation is predominantly asynchronous, but the Platinum rule is not yet formally demonstrated because external communication is implemented inside the integration rather than in an external dependency.

## HTTP stack

`cloud.py` uses `aiohttp.ClientSession` and exposes asynchronous methods for login, discovery, provisioning, and requests. Blocking certificate and filesystem operations are moved to `asyncio.to_thread`.

## SIP stack

`sip_client.py` uses:

- `asyncio.open_connection`;
- `asyncio.StreamReader` and `StreamWriter`;
- async locks;
- async reader, keepalive, register, dialog, and command flows.

Certificate/context creation and filesystem checks are delegated to `asyncio.to_thread`.

## Remaining async concerns

Direct `asyncio.create_task` calls exist in:

- `support_debug.py`;
- `sip_client.py` keepalive, reader, and call-timeout tasks.

They appear to have explicit ownership and cleanup paths, but extraction to a library should include cancellation tests for:

- unload during register;
- unload during an active SIP transaction;
- cancellation during HTTP provisioning;
- writer-task cancellation with queued records;
- call-timeout cancellation after dialog termination.

## Rule decision

`async-dependency` remains `todo`.

Reason: Home Assistant states that this rule has no exceptions. The repository has no external communication dependency whose API can be independently proven asynchronous. The code itself is async-oriented, but that does not close the dependency rule under a conservative official interpretation.

## Completion evidence required

1. External communication package declared in `manifest.json`.
2. All network I/O removed from the Home Assistant integration layer.
3. Public package API is async end to end.
4. No thread executor is used for network communication.
5. Cancellation and cleanup tests pass.
6. Dependency version is pinned and transparent.
