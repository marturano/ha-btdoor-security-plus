# Event Contract

## Public Home Assistant event

The integration emits `btdoor_security_plus_event` for externally consumable integration events.

Gate-action events currently include:

- `gate_open_requested`
- `gate_open_succeeded`
- `gate_open_failed`

Common correlation fields include `entry_id`, `gateway_id`, `request_id`, `source`, `reason` and `requested_at`.

## Normalized runtime events

The internal runtime event model is immutable and versioned with:

- `event_type`
- `source`
- `payload`
- `schema_version`
- `event_id`
- `timestamp`

Current normalized types include integration lifecycle, SIP registration, call lifecycle, media lifecycle, TLS/cloud state, gate opening, doorbell, SDP and support-bundle events.

## Compatibility rules

1. Consumers must tolerate additive fields.
2. `schema_version` changes only when interpretation cannot remain backward compatible.
3. Diagnostics-only payloads are not public contracts.
4. Credentials, certificate material, raw authorization headers and unredacted personal data must never be placed on the Home Assistant event bus.
5. Automation triggers should filter by `event_type` and, for multi-gateway systems, `entry_id`.

## Example trigger

```yaml
automation:
  - alias: Notify gate command failure
    triggers:
      - trigger: event
        event_type: btdoor_security_plus_event
        event_data:
          event_type: gate_open_failed
    actions:
      - action: persistent_notification.create
        data:
          title: BTDoor gate command failed
          message: >-
            Request {{ trigger.event.data.request_id }} failed:
            {{ trigger.event.data.error | default('unknown error') }}
```

## Related code

- `custom_components/btdoor_security_plus/event_bus/events.py`
- `custom_components/btdoor_security_plus/event_bus/mapper.py`
- `custom_components/btdoor_security_plus/services.py`
