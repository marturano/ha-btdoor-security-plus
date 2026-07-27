# Device and Entity Model

## Root and logical devices

Each config entry creates a stable root gateway identifier. Logical devices group entities by responsibility. Current `DeviceKind` responsibilities include gateway, Cloud, SIP, dialog/call manager, multimedia, diagnostics and the independent voice bridge.

## Identity contract

- Device identifiers include the stable config-entry identity.
- Entity unique IDs are stable across upgrades and naming changes.
- User-assigned names and areas are never overwritten merely to apply new translations.
- Logical devices may use `via_device` to the physical gateway only when the relationship is real.
- `DeviceKind.VOICE_BRIDGE` intentionally has no `via_device` parent because it is a virtual assistant-facing control surface, not a physical gateway component.

## Gate entities

- `button.apri_cancello` is the native one-shot Home Assistant action.
- `switch.apri_cancello_alexa` is an optional momentary assistant bridge and returns to off without issuing a second command.
- The gate is not modeled as a `cover` in 1.1.

## Visibility

Operational entities may be enabled by default. Developer and advanced-diagnostic entities are governed by Developer Mode and must not be exposed to external assistants.
