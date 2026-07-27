# Getting started

## Installation
Install BTDoor Security+ through HACS as a custom repository or copy `custom_components/btdoor_security_plus` into your Home Assistant configuration. Restart Home Assistant, then open **Settings → Devices & services → Add integration** and select BTDoor Security+.

## Configuration
Use the same owner-authorized MyHomeWeb account used by the official Door Entry application. Select the intended gateway and complete SIP provisioning. Do not copy identities, certificates or credentials from another installation.

## First verification
Confirm that the gateway and logical devices appear only once. Check Cloud and SIP entities, then press `button.apri_cancello` only when it is safe to operate the physical gate. Setup, reload and restart must never open the gate automatically.

Enable Developer Mode or Support Debug only while troubleshooting. Support Bundles are sanitized but should still be treated as private.
