# BTDoor Security+ 6.0.0

BTDoor Security+ 6.0.0 is the stable promotion of the validated 6.0.0-rc.3g build.

## Validation summary

- Health Score: 100/100.
- Cloud authentication and gateway discovery: operational.
- SIP registration: successful.
- TLS runtime: operational with TLS 1.3.
- Italian Device Registry names: validated.
- User-defined device names: preserved.
- Device IDs and parent-child associations: unchanged.
- Duplicate devices: none detected.
- Device software metadata: aligned to 6.0.0.

## Release scope

This release contains no new features or runtime changes compared with 6.0.0-rc.3g. Only release metadata, documentation, changelog entries, and version consistency tests were updated for the stable release.

## Upgrade

Install through HACS or replace the existing `custom_components/btdoor_security_plus` directory, restart Home Assistant, and reload the integration. Existing entities, automations, dashboards, areas, device associations, and user-assigned names are preserved.
