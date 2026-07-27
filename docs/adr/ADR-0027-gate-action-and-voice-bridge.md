# ADR-0027 — Native gate action and separate voice bridge

Status: Accepted.

## Decision
Use a button for the native one-shot gate action and an optional momentary switch on a separate `DeviceKind.VOICE_BRIDGE` virtual device for Alexa/Google discovery. Do not model the gate as a cover.

## Safety
Both surfaces delegate to one exact-entry backend. Off does nothing. No blind retry or lifecycle-triggered command is permitted.
