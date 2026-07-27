# Home Assistant Certification

This area contains the executable certification pack for BTDoor Security+ on a real Home Assistant 2026.x target.

The repository can prepare and validate a certification run, but it cannot claim runtime certification without connecting to an actual instance and preserving operator-reviewed evidence.

## Commands

```bash
python tools/home_assistant_certification/ha_certification.py init --run-id <id>
HA_URL=https://homeassistant.local:8123 HA_TOKEN=<token> python tools/home_assistant_certification/ha_certification.py probe --run-id <id>
python tools/home_assistant_certification/ha_certification.py validate --run-id <id>
python tools/home_assistant_certification/ha_certification.py export-target --run-id <id>
```

The exported result is an input for the existing Target Validation Pack and does not itself approve publication.
