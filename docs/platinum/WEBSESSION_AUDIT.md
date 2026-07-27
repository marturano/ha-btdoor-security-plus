# WebSession Injection Audit

> **Document status:** Historical / informational  
> **Normative:** No  
> **Active roadmap scope:** Excluded  
> **Current policy:** GOLD is the permanent governed maximum. This document is retained only as historical engineering evidence.


## Current implementation

`BticinoCloudClient` requires an `aiohttp.ClientSession` in its constructor:

```python
class BticinoCloudClient:
    def __init__(self, session: ClientSession, *, email: str, password: str, ...):
        self._session = session
```

The Home Assistant session is injected through `async_get_clientsession(...)` in all identified construction paths:

- `__init__.py` certificate/provisioning lifecycle;
- `config_flow.py` validation and provisioning;
- `developer.py` cloud diagnostics.

No direct `aiohttp.ClientSession()` construction was found.

## Audit result

The **technical session-injection pattern is already compliant**.

The rule remains open only because Home Assistant describes this as a capability of the integration dependency. The current HTTP client is internal to the custom component, not an external client package.

## Required completion path

When extracting the client library:

1. keep `ClientSession` as a required constructor argument, or an explicitly injected optional argument;
2. never close the shared Home Assistant session from the library;
3. document session ownership;
4. add tests proving no private session is created;
5. inject `async_get_clientsession(hass)` from setup, config flow, reauthentication, reconfigure, and diagnostics;
6. use a dedicated HA-created session only if cookie isolation is demonstrated as required.

## Estimated effort

Low after the external package boundary is created. Most implementation behaviour already exists.
