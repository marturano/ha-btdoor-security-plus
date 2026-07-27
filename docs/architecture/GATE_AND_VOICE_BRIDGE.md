# Gate Action and Voice Bridge

## Physical-action contract

Opening the gate is a security-sensitive, non-idempotent action. It requires an explicit entity press, service call, Assist intent or assistant command. The backend resolves exactly one config entry and emits requested/succeeded/failed audit events.

## No blind retry

Timeouts and transport errors are reported, not automatically retried. A late gateway response can make a retry unsafe. Setup, reload, restart, migration, entity restoration and Support Bundle generation cannot invoke the action.

## Native Home Assistant surface

`button.apri_cancello` is the canonical entity. Dashboards must use `button.press`; they must not reference historical `cover.btdoor_template_gate` or `cover.open_cover` actions.

## Alexa and Google bridge

`switch.apri_cancello_alexa` exists only to provide a discoverable assistant control. It is placed on the dedicated `Alexa / Google Gate Bridge` device. Turning it on delegates once to the canonical backend and then restores off. Turning it off never closes or reopens anything.

Alexa discovery and execution were confirmed after RC.7. Google Assistant remains unverified until tested on a real account/device; architecture support is not equivalent to validation.
