# BTDoor Security+

Custom integration for Home Assistant 2026.7 that connects a BTicino 300X door-entry gateway through MyHomeWeb cloud provisioning and a persistent SIP/TLS runtime.

> Release: **6.0.1 Stable**. Maintenance release correcting SIP timeline classification in diagnostic Support Bundles; operational Cloud, SIP, TLS, media and gate-control behavior is unchanged.

## Main capabilities

- UI configuration, reauthentication and reconfiguration.
- Automatic plant and gateway discovery.
- SIP certificate provisioning and renewal.
- Persistent SIP/TLS registration and gate-opening control.
- Incoming-call, dialog and media runtime observability.
- Persistent Runtime Event Bus and Call Journal.
- Redacted diagnostics and downloadable Support Bundles.
- Logical Home Assistant device model for gateway, cloud, SIP, dialog, media and diagnostics.
- Alexa/Alexa+ compatible momentary switch for gate opening.
- English, Italian, French, German and Spanish translations.

## Installation with HACS

1. Add this repository as a custom **Integration** repository in HACS.
2. Install **BTDoor Security+**.
3. Restart Home Assistant.
4. Open **Settings → Devices & services → Add integration** and search for BTDoor Security+.

The repository follows the HACS integration layout: all runtime files are under `custom_components/btdoor_security_plus`.

## Manual installation

Copy `custom_components/btdoor_security_plus` into your Home Assistant `/config/custom_components` directory and restart Home Assistant.

## Configuration

The config flow asks for MyHomeWeb credentials and the SIP device name. The integration discovers compatible gateways and provisions the required client certificate. Existing entries can be updated through **Reconfigure**.

## Home Assistant actions

The integration includes actions for gate opening, connection tests, call rejection, statistics reset, support-bundle generation, developer diagnostics, and Call Journal clear/export/rebuild operations. Action schemas and UI descriptions are defined in `services.yaml`.

## Operations and diagnostics

- Runtime health is exposed through native entities.
- The Support Bundle contains normalized runtime state, events, media history and Call Journal data.
- Sensitive credentials, certificate material and private keys are excluded or redacted.
- A starter Lovelace view is available in `dashboards/btdoor_operations.yaml`.

See `docs/OPERATIONS_DASHBOARD.md` and `docs/QUALITY_AND_RELEASE.md` for operational and release details.

## Logical device topology

Each configuration entry is represented as `Bticino DS+ Suite`, with the runtime devices linked below it through Home Assistant `via_device` relationships:

```text
Bticino DS+ Suite
├── Stato Cloud (Cloud Status)
├── Monitor SIP (SIP Monitor)
├── Monitor Chiamate (Call Manager)
├── Monitor Multimediale (Multimedia Monitor)
└── Diagnostica Avanzata (Developer Mode only)
```

`Riepilogo ultima chiamata` belongs to **Monitor Chiamate**. Its entity unique ID is unchanged, so upgrading does not require dashboard or automation changes. Media-only entities remain assigned to **Monitor Multimediale**.

## Voice assistants

The momentary gate-opening switch can be exposed through Home Assistant Cloud or the native Alexa/Google Assistant integrations. Restrict exposure to the intended household and require voice PIN protection where supported, because opening a gate is a security-sensitive action.

## Security notes

Certificate and private-key files are stored under the integration certificate directory. Back up this directory before replacing the integration manually. Never publish Support Bundles without reviewing their contents.

## Supported Home Assistant version

This release targets Home Assistant **2026.7.0 or newer**.

## Development

The repository includes pytest regression tests, Ruff and mypy configuration, HACS validation, Hassfest validation and release-package workflows.

## License and protocol notice

The project is released under the MIT License. See `LICENSE`.

BTDoor Security+ is an independent community project and is not affiliated with BTicino or Legrand.


## Developer Mode

Enable it from **Settings → Devices & services → BTDoor Security+ → Configure**. The integration reloads the config entry and exposes diagnostic-only controls and sensors for the runtime snapshot, the latest canonical events, Event Bus metrics, self-tests, support reports, and sanitized debug exports. Developer Mode is disabled by default and never exports credentials, tokens, certificates, or complete SIP identities.

When Developer Mode is disabled, the `Diagnostica Avanzata` device and all entities assigned to it are removed from the Home Assistant device and entity registries. Re-enabling Developer Mode recreates the diagnostic surface after the automatic Config Entry reload.

## Support Bundle privacy

Starting with 6.0.0, every structured support export is processed by one central
sanitizer before it is serialized. Home Assistant entry/device identifiers are
replaced with stable short hashes, the BTicino gateway identifier is partially
masked, and credentials, tokens, certificates, private keys and SIP correlation
identifiers are removed or anonymized. Operational booleans and counters remain
available for troubleshooting.


## Module visibility

Open **Settings → Devices & services → BTDoor Security+ → Configure** to control the interface modules independently. Each option includes an explanatory description. Stato Cloud, Monitor SIP, Monitor Chiamate and Monitor Multimediale are enabled by default in Italian installations. Diagnostica Avanzata is displayed only when both **Show Advanced Diagnostics** and **Developer mode** are enabled. Hiding a module removes its entities and device from Home Assistant without stopping the internal communication runtime.
