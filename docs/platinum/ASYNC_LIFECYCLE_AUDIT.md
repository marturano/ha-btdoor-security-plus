# Async and Lifecycle Audit

> **Document status:** Historical / informational  
> **Normative:** No  
> **Active roadmap scope:** Excluded  
> **Current policy:** GOLD is the permanent governed maximum. This document is retained only as historical engineering evidence.


## Positive evidence

- Home Assistant shared HTTP session is injected.
- Filesystem/certificate work is generally offloaded with `asyncio.to_thread` or `hass.async_add_executor_job`.
- Platform setup/unload uses config-entry forwarding APIs.
- Entity listeners are generally registered through `async_on_remove`.
- Entry runtime data owns event, renewal, debug, client, journal, and API resources.
- SIP reader/keepalive/call timeout tasks have explicit fields rather than anonymous fire-and-forget usage.

## Audit observations

Direct task creation occurs in the SIP client and support debug writer. This is acceptable only if every task has deterministic cancellation, awaiting, and exception retrieval.

UDP socket allocation in `media.py` is synchronous. The operations are short local socket operations, but runtime validation should confirm they cannot block the event loop under platform-specific failure modes.

## Required Platinum verification

- cancellation matrix for every owned task;
- unload during each lifecycle stage;
- no pending-task warnings after unload;
- no leaked sockets or writers;
- no listener callbacks after entry unload;
- no I/O on the event loop beyond bounded local operations;
- test under Home Assistant's asyncio debug/blocking-call detection.

## Result

No immediate critical lifecycle defect was proven by this static audit. This area is a validation requirement, not the primary Platinum blocker.
