# ADR-0021: Runtime Event Producer Wiring

## Status
Accepted for 5.0.0-beta.4.1.

## Context
The Runtime Event Bus introduced in beta.4 retained only `integration_started` when no new call occurred after installation. The first SIP REGISTER also completed before the Home Assistant listener was attached. Some media mappings did not match the notification names actually emitted by the SIP/media runtime.

## Decision
The SIP dispatcher emits an explicit `invite_received` notification for each new dialog. The event mapper recognizes the concrete media notification names `media_session_prepared`, `media_session_closed`, and `media_session_failed`. Setup publishes synchronized SIP and Cloud state events after the listener and per-entry event bus are available.

## Consequences
A new call produces a deterministic event sequence suitable for the Call Journal and future realtime dashboards. Initial registration and Cloud state are observable even if they were established before event subscribers were registered.
