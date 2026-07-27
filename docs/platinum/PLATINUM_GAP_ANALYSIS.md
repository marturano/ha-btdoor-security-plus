# Platinum Gap Analysis

> **Document status:** Historical / informational  
> **Normative:** No  
> **Active roadmap scope:** Excluded  
> **Current policy:** GOLD is the permanent governed maximum. This document is retained only as historical engineering evidence.


## Scope

QS-22 is a documentation-only audit of the QS-21 repository. It does not change integration runtime code, dependencies, entities, services, translations, or behaviour.

The audit uses the Home Assistant Integration Quality Scale Platinum rules current for the 2026 documentation set:

- `async-dependency`
- `inject-websession`
- `strict-typing`

It also evaluates the Home Assistant development requirement that communication with external devices or services be isolated in an external Python package.

## Executive conclusion

The repository is **not ready to claim Platinum**.

| Rule | Current evidence | Audit result |
|---|---|---|
| `async-dependency` | HTTP and SIP implementations are asynchronous, but live inside the custom integration; manifest contains no external communication client library | **Not proven** |
| `inject-websession` | `BticinoCloudClient` accepts `aiohttp.ClientSession`; all three construction paths inject `async_get_clientsession(...)` | **Implementation pattern present, rule not formally closable until the communication dependency boundary is resolved** |
| `strict-typing` | mypy configuration is non-strict; integration alias is `ConfigEntry[Any]`; static audit found material untyped surface | **Not complete** |

## Main architectural blocker

The integration directly contains both communication stacks:

- MyHomeWeb HTTP API client in `cloud.py`;
- SIP/TLS client in `sip_client.py`.

The manifest declares only `asn1crypto==1.5.1`. It does not declare an external client dependency that owns communication with BTicino services and devices.

For a conservative Home Assistant Core/official Platinum interpretation, the communication code should be moved to a separately versioned Python package hosted on PyPI, with:

- source distribution;
- public issue tracker;
- fully asynchronous API;
- injected `aiohttp.ClientSession`;
- PEP-561 `py.typed` marker;
- typed public models and exceptions;
- unit and transport tests independent of Home Assistant.

## Measured typing baseline

Static AST and source scans of the integration produced:

- 77 Python modules;
- 128 asynchronous functions;
- 410 synchronous functions;
- 65 parameters without annotations;
- 94 functions without explicit return annotations;
- 172 AST references to `Any`;
- 210 textual `Any` occurrences;
- zero `type: ignore` comments;
- zero `cast(...)` calls.

The largest typing concentration is in:

1. `sensor.py` — many compact property definitions with omitted return types;
2. `developer.py` — diagnostics/support payloads represented with `Any`;
3. `support_models.py`;
4. `cloud.py`;
5. `runtime_state/provider.py`;
6. `config_flow.py`.

The current alias is:

```python
type BticinoConfigEntry = ConfigEntry[Any]
```

For Platinum this should become a custom typed config entry using the concrete runtime data type and should be used throughout the integration.

## Risk assessment

| Workstream | Complexity | Regression risk | Release recommendation |
|---|---:|---:|---|
| External async client package | High | High | Do not include in 1.1.0 Final |
| WebSession contract formalization | Low after extraction | Low | Implement with client package |
| Strict typing integration | Medium/High | Medium | Incremental, gated by mypy |
| Strict typing client package | Medium | Medium | Implement from package inception |
| Async lifecycle cleanup | Low/Medium | Medium | Validate during extraction |
| Public API rationalization | Medium | Medium | Optional; avoid unrelated changes |

## Recommendation

Preserve QS-21 Gold for the 1.1 release line. Plan Platinum as a dedicated 1.2 architectural programme with separate client-library extraction and a strict typing gate. Do not mix this refactor into the final stabilization of 1.1.0.
