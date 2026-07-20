# Migration from alpha.19 to alpha.20

Version 4.0.0-alpha.20 changes the Home Assistant domain and is intentionally a
breaking alpha release.

1. Back up Home Assistant.
2. Record the current integration options and entity customizations.
3. Remove the old **BTDoor entry plus** config entry from Home Assistant.
4. Stop Home Assistant.
5. Remove `custom_components/btdoor_entry_plus`.
6. Install `custom_components/btdoor_security_plus` from this release.
7. Start Home Assistant and add **BTDoor Security+** again.
8. Replace service calls such as `btdoor_entry_plus.open_gate` with
   `btdoor_security_plus.open_gate`.
9. Replace event triggers using `btdoor_entry_plus_event` with
   `btdoor_security_plus_event`.

Certificate files are now stored under the new component directory. Copy only
the certificate files required by the integration; never publish private keys.
