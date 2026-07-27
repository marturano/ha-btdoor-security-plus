# Error Contract

## Categories

| Category | Expected caller behavior |
|---|---|
| Target resolution | Correct `entry_id` or `entity_id`; never retry against another gateway automatically. |
| Validation | Fix malformed or unsupported input. |
| Authentication/certificate | Reconfigure credentials or certificate material; do not retry rapidly. |
| Connectivity/timeout | Retry with bounded backoff when appropriate. |
| SIP/device rejection | Surface the failure and preserve the device response code when available. |
| Developer-mode restriction | Enable developer mode only for explicit diagnostic work. |

## Physical action failures

`open_gate` returns a normalized failure payload for known SIP and timeout failures and emits `gate_open_failed`. Unknown programming/runtime failures are not converted into success-like responses.

## Logging and privacy

Errors must be actionable but sanitized. Secrets, private keys, bearer tokens, full certificate contents and raw media must not be included in normal logs or event payloads.
