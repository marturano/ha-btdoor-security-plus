# Automation Examples

## Open one explicit gate

```yaml
script:
  open_front_gate:
    alias: Open front gate
    sequence:
      - action: btdoor_security_plus.open_gate
        data:
          entity_id: button.front_gate_open
          reason: Approved Home Assistant script
          source: script
        response_variable: gate_result
      - action: logbook.log
        data:
          name: BTDoor
          message: "Gate request result: {{ gate_result }}"
```

## Doorbell announcement through another integration

```yaml
automation:
  - alias: Announce BTDoor doorbell
    triggers:
      - trigger: event
        event_type: btdoor_security_plus_event
        event_data:
          event_type: doorbell_pressed
    actions:
      - action: notify.alexa_media
        data:
          target: media_player.entry_echo
          message: Someone rang the doorbell
          data:
            type: announce
```

The notification action above belongs to the separately installed assistant/media integration; BTDoor Security+ only supplies the event.

## Safety note

Do not create an automation that opens a gate solely because an AI provider reports a known face, vehicle or object.
