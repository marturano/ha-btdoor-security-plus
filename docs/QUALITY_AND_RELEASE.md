# Quality and release policy

## Release status

`6.0.1` is a diagnostics-only maintenance release based on the validated 6.0.0 Stable runtime. It corrects SIP timeline summary classification while preserving Cloud, SIP/TLS, Event Bus, Support Bundle, Call Journal, gate control and Device Registry behavior.

## Quality matrix

| Area | Status | Evidence |
|---|---|---|
| Config flow | Implemented | `config_flow.py` |
| Reauthentication | Implemented | `async_step_reauth*` |
| Reconfiguration | Implemented | `async_step_reconfigure` |
| Diagnostics | Implemented | `diagnostics.py` and Support Bundle framework |
| Repair issues | Partial | Missing-certificate repair issue implemented; guided repair flows remain future work |
| Device registry | Implemented | `device_model/` |
| Entity translations | Implemented | `strings.json`, `translations/` |
| Runtime data | Implemented | typed config-entry runtime data |
| Event-driven updates | Implemented | Runtime Event Bus and push listeners |
| Tests | Implemented, expanding | `tests/` |
| Strict typing | In progress | mypy configuration added; full clean run is a later gate |
| HACS validation | Automated | `.github/workflows/validate.yml` |
| Release packaging | Automated | `.github/workflows/release.yml` |

This repository does not claim an official Home Assistant Quality Scale tier. The matrix records implemented behavior and remaining work for a custom integration.

## Release gates

Every release should pass:

1. Python bytecode compilation.
2. JSON parsing for manifest, strings, translations, icons and HACS metadata.
3. Regression tests.
4. HACS validation.
5. Hassfest validation.
6. Installation and restart on the supported Home Assistant release.
7. A real incoming-call test followed by Support Bundle review.

## Version consistency

The manifest and `INTEGRATION_VERSION` must match. Runtime diagnostics and startup events use `INTEGRATION_VERSION`; release automation verifies the manifest while packaging.

## Export sanitization policy (6.0.0)

Every structured Support Bundle export passes through the centralized
`support_sanitizer.py` policy before serialization. Standard exports hash
persistent Home Assistant identifiers, partially mask the gateway identifier,
remove secrets and cryptographic material, and retain only the operational
booleans and counters required for diagnosis. Raw runtime objects must never be
written directly to an export archive.
