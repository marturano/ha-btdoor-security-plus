# WebSocket API — Planned

## Status

Contract-only roadmap item for the 3.x Developer Platform. RC.15 does not register BTDoor-specific WebSocket commands.

## Design requirements

- explicit command and subscription versions;
- authenticated Home Assistant connection;
- event filtering by config entry/device;
- bounded queues and backpressure;
- resumable correlation identifiers where feasible;
- sanitized payloads;
- cancellation and unsubscribe lifecycle;
- schema and conformance tests.

Internal dispatcher signals and Home Assistant's generic event subscriptions are not public BTDoor WebSocket commands.
