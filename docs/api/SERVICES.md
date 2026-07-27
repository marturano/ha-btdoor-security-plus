# Action and Service Contract

## Status

The integration domain is `btdoor_security_plus`. Home Assistant UI may label services as actions; YAML continues to use `action: btdoor_security_plus.<name>` or the compatible service-call form.

## Targeting rules

- `open_gate` requires one unambiguous loaded configuration. Supply `entry_id` or a BTDoor `button` `entity_id` when multiple gateways exist.
- Other maintenance actions may operate on all loaded entries when `entry_id` is omitted.
- Broad fallback routing is forbidden for physical security commands.
- Invalid or unloaded targets must fail visibly rather than silently selecting another gateway.

## Registered actions

| Action | Response | Key fields | Contract |
|---|---|---|---|
| `open_gate` | Optional response | `entry_id`, `entity_id`, `reason`, `source` | Sends the validated gate command, emits request/result events and returns an entry-keyed result when requested. |
| `reset_statistics` | None | `entry_id` | Resets runtime counters and persisted statistics. |
| `test_connection` | None | `entry_id` | Tests certificate/TLS/SIP connectivity without opening the gate. |
| `reject_call` | None | `entry_id` | Rejects the current ringing call. |
| `developer_test` | Optional response | `entry_id`, `test` | Developer-mode diagnostics only. |
| `generate_support_report` | Optional response | `entry_id`, `include_logs` | Produces redacted support artifacts. |
| `export_debug_bundle` | Optional response | `entry_id`, `include_logs` | Alias for developer workflows. |
| `clean_debug_environment` | Optional response | `entry_id` | Removes generated debug artifacts while retaining configuration and certificates. |
| `clear_call_journal` | Optional response | `entry_id` | Permanently clears call-journal records. |
| `export_call_journal` | Optional response | `entry_id` | Writes private JSON under the integration config directory; no `/local` URL is created. |
| `rebuild_call_journal` | Optional response | `entry_id` | Rebuilds the journal from retained normalized events. |

## `open_gate` response

The response is keyed by config-entry ID. Result fields may include:

- `entry_id`
- `gateway_id`
- `request_id`
- `reason`
- `source`
- `requested_at`
- `event_type`
- `success`
- `status`
- `code`
- `duration_ms`
- `error` on failure

Consumers must tolerate additional fields. `request_id` is the correlation key between request, success and failure events.

## Safety baseline

Automations should include deliberate user intent, context and rate limiting. Biometric or AI classification alone must never invoke `open_gate`.

## Source of truth

- Schema/UI metadata: `custom_components/btdoor_security_plus/services.yaml`
- Runtime registration: `custom_components/btdoor_security_plus/services.py`
- Constants: `custom_components/btdoor_security_plus/const.py`
