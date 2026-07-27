# Runtime support evidence — 2026-07-27

Source: operator-provided `BTDoorSecurityPlus_Support_20260727-081525.zip`.

Only selected, already-redacted JSON artifacts are retained. Raw logs, registry exports, configuration, SDP and event history are intentionally excluded from the repository evidence set.

## Demonstrated

- integration version `1.1.0-rc.15`;
- support schema 3;
- runtime health score 100/100;
- cloud authentication and configured gateway available;
- certificate and private key available;
- SIP registration returned 200;
- live TLS 1.3 session established;
- media and dialog lifecycle observable and closed cleanly;
- no reported runtime error and zero dropped debug records;
- translation report captured.

## Not demonstrated by this bundle

- exact Home Assistant Core version;
- clean setup, reload, restart recovery and entity continuity;
- measured startup/reload/memory thresholds;
- HACS clean install, upgrade and rollback;
- complete runtime-security sign-off, including server-verification disposition;
- interactive UX/accessibility review.

This evidence is therefore supporting evidence only and does not close the blocking target-validation records.
