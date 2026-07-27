# Feature Recovery and Future Evolution Review — RC.12

## Executive conclusion

A second code-to-documentation comparison found no missing large runtime subsystem, but it did find several features or obligations that were either absent from the active feature matrix or described at the wrong roadmap level.

## Implemented features that must be documented explicitly

| Capability | Code evidence | Correct product treatment |
|---|---|---|
| Reject current call | `btdoor_security_plus.reject_call` service | Limited 1.1 action; does not imply answer/end-call or bidirectional audio |
| Call Journal maintenance | clear, export and rebuild services | 1.1 operational capability; exports remain private |
| Connection test and statistics reset | integration services | 1.1 diagnostic/maintenance capability |
| Developer test and Support Bundle actions | services and diagnostic buttons | 1.1 Developer Mode only |
| Event entity and normalized runtime events | event platform/event bus | 1.0 Foundation retained in 1.1 |
| Managed Assist sentence installation | sentence manager and repair notification | 1.1 operational capability with user-file ownership safeguards |
| Retained media-session summaries | media persistence and sensors | Diagnostic metadata only; not Video Core or Audio Control |
| Exact entity-based service targeting | service resolver | Required multi-entry safety contract |

## Real gaps before Stable

1. Certificate-expiry blueprint still lacks its required days-remaining sensor.
2. Full 2026.1–2026.7 exact-package CI matrix has not been executed.
3. Runtime validation is not recorded for every monthly line.
4. Google Assistant remains unverified on a real account/device.
5. Historical pytest stubs still prevent treating a full local collection as authoritative.
6. No single automated audit currently proves that Developer Mode entities are excluded from voice-assistant exposure guidance.
7. The limited `reject_call` action needs lifecycle and no-cross-entry regression tests.
8. Call Journal export permissions and non-`/local` placement need explicit regression tests.

## Future evolutions not currently committed to the roadmap

These are candidates, not approved milestones. They should be evaluated after the current 1.1–2.0 sequence unless they become prerequisites.

### Security and trust center

- certificate lifecycle dashboard and guided renewal;
- authorization/revocation inventory for every paired client;
- security posture score separate from operational Health Score;
- audit-log retention and signed export manifests;
- explicit privacy modes for cameras, microphones and cloud providers.

### Fleet and multi-site management

- multiple homes, gateways and account scopes in one installation;
- topology view, conflict detection and per-site health;
- bulk diagnostics without cross-entry command execution;
- import/export of sanitized site profiles.

### Backup, restore and disaster recovery

- portable integration backup excluding secrets by default;
- certificate/key restore workflow with owner confirmation;
- registry identity reconciliation after Home Assistant restore;
- pre-upgrade snapshot and automated rollback readiness checks.

### Local observability and performance

- Prometheus-compatible metrics or Home Assistant diagnostics metrics;
- bounded protocol traces with opt-in redaction profiles;
- latency, packet-loss and command-success service-level indicators;
- long-term trend entities that obey recorder/statistics requirements.

### Open event and automation API

- stable normalized event schema for third-party automations;
- versioned webhook/event subscriptions where justified;
- Node-RED and AppDaemon examples;
- explicit action correlation IDs across gate, calls, media and notifications.

### Accessibility and household safety

- visual, audible and haptic call alerts;
- accessibility-focused dashboards;
- child/guest/maintenance access profiles;
- emergency fallback behavior when cloud or SIP is unavailable.

### Protocol laboratory

- passive capability recorder for unknown firmware;
- deterministic replay of sanitized traces;
- adapter conformance suite;
- community-contributed device profiles without distributing credentials or secrets.

### Standards-based interoperability

- evaluation of Matter or future Home Assistant device APIs only where they fit door-entry semantics;
- ONVIF/WebRTC interoperability for authorized camera paths;
- provider-neutral notification and media handoff contracts.

## Items deliberately not promoted

General lighting, HVAC, energy, alarm-panel expansion and unrelated MyHOME families remain outside the product unless needed by the door-entry/security domain. Their presence in historical planning does not make them lost requirements.
